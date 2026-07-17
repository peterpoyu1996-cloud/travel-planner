"""組 prompt、透過 LLMProvider 把候選景點 + 使用者條件轉成逐日行程。

成本護欄：呼叫前 filters.select_candidates() 已把候選縮小到 <=15 筆，
prompt 不會隨知識庫規模成長。實際要不要花錢呼叫 API，由 llm_provider.get_llm_provider()
依有沒有 ANTHROPIC_API_KEY 決定（沒 key 就用不花錢的 StaticDemoProvider）。
"""

import json

from .filters import select_candidates
from .llm_provider import get_llm_provider
from .models import DayPlan, ItineraryResponse, TripConditions

SYSTEM_PROMPT = """你是沖繩旅遊行程規劃助手。根據使用者條件與提供的候選景點清單，安排逐日行程。

規則：
1. 只能使用候選清單中的景點，不可捏造清單以外的地點
2. 同一天的景點盡量在同一個 region_group（地理分群）內，避免本島南北來回跑
3. 每個景點附上一句推薦原因，需具體（提及親子適合度/停留時間/交通方式等已知資訊），不要用「很棒」這種空泛描述
4. 如果候選清單在某天明顯不足，於 warnings 欄位誠實說明，不要硬湊
5. 只回傳 JSON，不要有其他文字說明
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
    return ItineraryResponse(
        days=[DayPlan(**d) for d in parsed.get("days", [])],
        warnings=parsed.get("warnings", []),
    )
