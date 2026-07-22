"""POST /day-plan 的邏輯層：使用者已經自己決定每天要去哪些景點（不像 custom_route.py
是丟一包讓演算法全權分天），這裡只負責 1) 幫每天內部景點排最佳順序 2) 檢查使用者
選的天序（哪天先去）順不順，不順的話用 route_optimizer.evaluate_day_plan() 建議更好的
天序——天序建議只調換「哪天先去」，不會把使用者選的景點搬到別天去，那是使用者自己
的決定，不該被覆蓋。

跟 custom_route.py 共用起訖點解析（resolve_anchor）、預設停留時間常數
（DEFAULT_VISIT_MINUTES）跟知識庫載入方式，其餘邏輯獨立，不動 custom_route.py。
"""

from datetime import timedelta

from common.geo.route_optimizer import RoutePoint, evaluate_day_plan, parse_stay_minutes
from common.geo.stay_duration_defaults import estimate_default_stay_minutes

from .custom_route import DEFAULT_VISIT_MINUTES, resolve_anchor
from .filters import load_knowledge_base
from .models import DayPlan, DayPlanRequest, DayPlanResponse, ItineraryStop


def _build_day_plans(days: list[list[RoutePoint]], legs, kb_by_id: dict, start_date) -> list[DayPlan]:
    # 每個真實點都對應一段「進入它」的 leg（見 evaluate_day_plan 的 legs 攤平規則），
    # 用 to_id 查表組 travel_time_from_prev，不用重算
    leg_by_to_id = {leg.to_id: leg for leg in legs}

    plans: list[DayPlan] = []
    stop_number = 0
    for day_index, order in enumerate(days, start=1):
        stops: list[ItineraryStop] = []
        for position, point in enumerate(order, start=1):
            stop_number += 1
            entry = kb_by_id[point.id]
            name = entry.get("translated_name") or entry.get("name") or entry.get("name_local", "")
            leg = leg_by_to_id.get(point.id)
            travel_text = f"約{round(leg.minutes)}分鐘（{leg.detail}）" if leg else None
            stops.append(ItineraryStop(
                id=point.id,
                name=name,
                category=entry.get("category", ""),
                reason=f"第 {day_index} 天第 {position} 站，依實際車程排序",
                suggested_stay_duration=entry.get("suggested_stay_duration"),
                travel_time_from_prev=travel_text,
                parking_notes=entry.get("parking_notes"),
                requires_reservation=bool(entry.get("requires_reservation", False)),
            ))
        plans.append(DayPlan(
            day_index=day_index,
            date=start_date + timedelta(days=day_index - 1),
            stops=stops,
        ))
    return plans


def generate_day_plan(request: DayPlanRequest) -> DayPlanResponse:
    kb = load_knowledge_base()
    kb_by_id = {entry["id"]: entry for entry in kb}

    all_ids = [aid for day in request.days for aid in day.attraction_ids]
    unknown_ids = [i for i in all_ids if i not in kb_by_id]
    if unknown_ids:
        raise ValueError(f"未知的景點 id：{', '.join(unknown_ids)}")

    excluded = [i for i in all_ids if kb_by_id[i].get("lat") is None or kb_by_id[i].get("lng") is None]
    excluded_set = set(excluded)

    day_buckets: list[list[RoutePoint]] = []
    for day in request.days:
        valid_ids = [i for i in day.attraction_ids if i not in excluded_set]
        if not valid_ids:
            raise ValueError("某一天選的景點全部缺座標，無法排這一天，至少要留一個有座標的景點")

        bucket = []
        for poi_id in valid_ids:
            entry = kb_by_id[poi_id]
            stay = (
                parse_stay_minutes(entry.get("suggested_stay_duration"))
                or estimate_default_stay_minutes(entry)
                or DEFAULT_VISIT_MINUTES
            )
            bucket.append(RoutePoint(id=poi_id, lat=entry["lat"], lng=entry["lng"], suggested_stay_minutes=stay))
        day_buckets.append(bucket)

    start_lat, start_lng, _ = resolve_anchor(request.start, kb_by_id, default_label="起點")
    start_point = RoutePoint(id="__start__", lat=start_lat, lng=start_lng)

    end_point = None
    if request.end:
        end_lat, end_lng, _ = resolve_anchor(request.end, kb_by_id, default_label="終點")
        end_point = RoutePoint(id="__end__", lat=end_lat, lng=end_lng)

    result = evaluate_day_plan(day_buckets, start_point, end_point)

    chosen_days = _build_day_plans(result["chosen"]["days"], result["chosen"]["legs"], kb_by_id, request.start_date)

    suggested_days = None
    suggested_total_minutes = None
    if result["suggested_order"] is not None:
        suggested_days = _build_day_plans(result["suggested"]["days"], result["suggested"]["legs"], kb_by_id, request.start_date)
        suggested_total_minutes = result["suggested"]["total_minutes"]

    warnings = []
    if excluded:
        warnings.append(f"以下景點缺少座標，已從行程中排除：{', '.join(excluded)}")

    return DayPlanResponse(
        chosen_days=chosen_days,
        chosen_total_minutes=result["chosen"]["total_minutes"],
        suggested_order=result["suggested_order"],
        suggested_days=suggested_days,
        suggested_total_minutes=suggested_total_minutes,
        minutes_saved=result["minutes_saved"],
        warnings=warnings,
        excluded_attraction_ids=excluded,
    )
