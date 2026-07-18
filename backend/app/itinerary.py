"""組 prompt、透過 LLMProvider 把候選景點 + 使用者條件轉成逐日行程。

成本護欄：呼叫前 filters.select_candidates() 已把候選縮小到 <=15 筆，
prompt 不會隨知識庫規模成長。實際要不要花錢呼叫 API，由 llm_provider.get_llm_provider()
依有沒有 ANTHROPIC_API_KEY 決定（沒 key 就用不花錢的 StaticDemoProvider）。

travel_time_from_prev 不靠 LLM 生成（LLM 不擅長算距離，容易亂猜）：LLM 生成完
stop 順序後，用 common/geo/travel_time.py 的高速公路感知估算法，依候選資料的真實
座標重新算過、覆蓋掉這個欄位，數字是算出來的，不是模型掰的。
"""

import json

from common.geo.highway_routing import load_network
from common.geo.travel_time import estimate_minutes

from .filters import select_candidates
from .llm_provider import get_llm_provider
from .models import DayPlan, ItineraryResponse, TripConditions

SYSTEM_PROMPT = """你是沖繩旅遊行程規劃助手。根據使用者條件與提供的候選景點清單，安排逐日行程。

規則：
1. 只能使用候選清單中的景點，不可捏造清單以外的地點
2. 同一天的景點盡量在同一個 region_group（地理分群）內，避免本島南北來回跑
3. 每個景點附上一句推薦原因，需具體（提及親子適合度/停留時間/交通方式等已知資訊），不要用「很棒」這種空泛描述
4. 如果候選清單在某天明顯不足，於 warnings 欄位誠實說明，不要硬湊
5. 輸出的 stop.name 一律用候選資料的 translated_name 欄位（保證是中文），不要用 name 欄位
   （name 在候選資料裡沒把握翻譯正確時會是日文原文，不適合直接顯示給使用者看）
6. travel_time_from_prev 欄位不用填，系統會依真實座標另外算，你填了也會被覆蓋
7. 只回傳 JSON，不要有其他文字說明
"""


def build_user_prompt(conditions: TripConditions, candidates: list[dict]) -> str:
    trip_days = (conditions.end_date - conditions.start_date).days + 1
    return json.dumps(
        {
            "trip_days": trip_days,
            "start_date": str(conditions.start_date),
            "lodging": conditions.lodging,
            "has_car": conditions.has_car,
            "has_kids": conditions.has_kids,
            "kid_age_range": conditions.kid_age_range,
            "budget_level": conditions.budget_level,
            "start_location": conditions.start_location,
            "candidates": candidates,
            "output_schema": {
                "days": [{"day_index": "int", "date": "YYYY-MM-DD", "stops": [
                    {"id": "str", "name": "str", "category": "str", "reason": "str",
                     "suggested_stay_duration": "str|null", "travel_time_from_prev": "str|null",
                     "parking_notes": "str|null", "requires_reservation": "bool"}
                ]}],
                "warnings": ["str"],
            },
        },
        ensure_ascii=False,
    )


def fill_real_travel_times(days: list[DayPlan], candidates: list[dict]) -> None:
    """把整趟行程相鄰兩站的 travel_time_from_prev，改成用真實座標＋高速公路網路
    算出來的估計值，蓋掉 LLM 填的（or 沒填的）版本。原地修改 days。

    跨天也要算：前一天最後一站（通常是飯店）到隔天第一站，一樣是真實的一段車程，
    不能因為分屬不同 DayPlan 就跳過不算——把所有天的 stops 攤平成一條連續序列，
    只有整趟行程最開頭那一站沒有「前一站」。

    候選資料裡沒有座標的（大部分 source="osm" 的資料還沒補到 lat/lng）就跳過，
    保留原本的值——沒座標沒辦法算，不能假裝算得出來。
    """
    by_id = {c["id"]: c for c in candidates}
    graph, interchanges = load_network()

    all_stops = [stop for day in days for stop in day.stops]
    for i in range(1, len(all_stops)):
        prev_entry = by_id.get(all_stops[i - 1].id)
        curr_entry = by_id.get(all_stops[i].id)
        if not prev_entry or not curr_entry:
            continue
        if prev_entry.get("lat") is None or curr_entry.get("lat") is None:
            continue

        result = estimate_minutes(
            prev_entry["lat"], prev_entry["lng"],
            curr_entry["lat"], curr_entry["lng"],
            interchanges, graph,
        )
        all_stops[i].travel_time_from_prev = f"約{round(result['minutes'])}分鐘（{result['detail']}）"


def generate_itinerary(conditions: TripConditions) -> ItineraryResponse:
    candidates = select_candidates(conditions, limit=15)

    if not candidates:
        return ItineraryResponse(
            days=[],
            warnings=["知識庫中沒有符合條件的候選景點，請放寬條件或補充知識庫資料。"],
        )

    provider = get_llm_provider()
    text = provider.generate(SYSTEM_PROMPT, build_user_prompt(conditions, candidates))
    parsed = json.loads(text)
    days = [DayPlan(**d) for d in parsed.get("days", [])]
    fill_real_travel_times(days, candidates)

    return ItineraryResponse(
        days=days,
        warnings=parsed.get("warnings", []),
    )
