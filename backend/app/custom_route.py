"""POST /custom-route 的邏輯層：把使用者指定的景點 id + 天數 + 起訖點，丟給
common/geo/route_optimizer.py 算出最小車程排序並依天數切分。

跟 backend/app/itinerary.py 刻意不共用邏輯（那條路徑是 LLM 決定順序、事後補車程；
這裡反過來，順序本身就是演算法算出來的），只共用知識庫載入（filters.load_knowledge_base）
跟 common/geo/ 底層——itinerary.py/filters.py/llm_provider.py 完全不用改。
"""

from datetime import timedelta

from common.geo.route_optimizer import RoutePoint, optimize_route, parse_stay_minutes, split_into_days
from common.geo.stay_duration_defaults import estimate_default_stay_minutes

from .filters import load_knowledge_base
from .models import CustomRouteRequest, CustomRouteResponse, DayPlan, GeoAnchor, ItineraryStop

DEFAULT_VISIT_MINUTES = 60.0  # suggested_stay_duration 解析不出來、且比對不到
                               # stay_duration_defaults 任何類別關鍵字時的最後防線，
                               # 只用來讓 split_into_days 的天數平衡合理，不對外顯示、
                               # 不當成事實填回任何欄位

_START_ID = "__start__"
_END_ID = "__end__"


def resolve_anchor(anchor: GeoAnchor, kb_by_id: dict, default_label: str) -> tuple[float, float, str]:
    """回傳 (lat, lng, label)。poi_id 給的話查知識庫拿座標——查無此 id、或該筆缺座標，
    都當成使用者輸入錯誤（ValueError，回 422），跟「已知景點但缺座標」這種資料品質
    情境（softwarning 排除掉，不是硬錯誤）是兩回事：起訖點沒有座標就完全無法算路線，
    不像中途景點可以跳過。
    """
    if anchor.poi_id is not None:
        entry = kb_by_id.get(anchor.poi_id)
        if entry is None:
            raise ValueError(f"起訖點指定的景點 id 不存在：{anchor.poi_id}")
        if entry.get("lat") is None or entry.get("lng") is None:
            raise ValueError(f"起訖點指定的景點缺少座標，無法當路線起訖點：{anchor.poi_id}")
        label = entry.get("translated_name") or entry.get("name") or anchor.poi_id
        return entry["lat"], entry["lng"], label

    # GeoAnchor 的 model_validator 已經保證這個分支下 lat/lng 一定有值
    return anchor.lat, anchor.lng, anchor.label or default_label


def _empty_days(request: CustomRouteRequest) -> list[DayPlan]:
    return [
        DayPlan(day_index=i + 1, date=request.start_date + timedelta(days=i), stops=[])
        for i in range(request.trip_days)
    ]


def generate_custom_route(request: CustomRouteRequest) -> CustomRouteResponse:
    kb = load_knowledge_base()
    kb_by_id = {entry["id"]: entry for entry in kb}

    unknown_ids = [i for i in request.attraction_ids if i not in kb_by_id]
    if unknown_ids:
        raise ValueError(f"未知的景點 id：{', '.join(unknown_ids)}")

    excluded = [
        i for i in request.attraction_ids
        if kb_by_id[i].get("lat") is None or kb_by_id[i].get("lng") is None
    ]
    valid_ids = [i for i in request.attraction_ids if i not in excluded]

    if not valid_ids:
        return CustomRouteResponse(
            days=_empty_days(request),
            warnings=["所選景點都缺少座標，無法計算路線"],
            total_travel_minutes=0.0,
            excluded_attraction_ids=excluded,
        )

    start_lat, start_lng, _ = resolve_anchor(request.start, kb_by_id, default_label="起點")
    end_anchor = resolve_anchor(request.end, kb_by_id, default_label="終點") if request.end else None

    points = [RoutePoint(id=_START_ID, lat=start_lat, lng=start_lng, suggested_stay_minutes=0.0)]
    for poi_id in valid_ids:
        entry = kb_by_id[poi_id]
        stay = (
            parse_stay_minutes(entry.get("suggested_stay_duration"))
            or estimate_default_stay_minutes(entry)
            or DEFAULT_VISIT_MINUTES
        )
        points.append(RoutePoint(id=poi_id, lat=entry["lat"], lng=entry["lng"], suggested_stay_minutes=stay))
    if end_anchor:
        points.append(RoutePoint(id=_END_ID, lat=end_anchor[0], lng=end_anchor[1], suggested_stay_minutes=0.0))

    result = optimize_route(points, start_id=_START_ID, end_id=_END_ID if end_anchor else None)
    order = result["order"]
    legs = result["legs"]

    # travel_time_from_prev：每個「真實」點都要對應到「進入它」的那段 leg，不論上一站
    # 是不是虛擬起訖點（例如飯店到第一個景點的車程，使用者仍然想看到）。
    travel_time_by_id: dict[str, str] = {}
    for i in range(1, len(order)):
        leg = legs[i - 1]
        travel_time_by_id[order[i].id] = f"約{round(leg.minutes)}分鐘（{leg.detail}）"

    day_chunks = split_into_days(order, legs, request.trip_days)

    days: list[DayPlan] = []
    stop_number = 0
    for day_index, chunk in enumerate(day_chunks, start=1):
        stops: list[ItineraryStop] = []
        for point in chunk:
            if point.id in (_START_ID, _END_ID):
                continue
            stop_number += 1
            entry = kb_by_id[point.id]
            name = entry.get("translated_name") or entry.get("name") or entry.get("name_local", "")
            stops.append(ItineraryStop(
                id=point.id,
                name=name,
                category=entry.get("category", ""),
                reason=f"路線最佳化第 {stop_number} 站，依實際車程排序，非人工挑選",
                suggested_stay_duration=entry.get("suggested_stay_duration"),
                travel_time_from_prev=travel_time_by_id.get(point.id),
                parking_notes=entry.get("parking_notes"),
                requires_reservation=bool(entry.get("requires_reservation", False)),
            ))
        days.append(DayPlan(
            day_index=day_index,
            date=request.start_date + timedelta(days=day_index - 1),
            stops=stops,
        ))

    warnings = []
    if excluded:
        warnings.append(f"以下景點缺少座標，已從路線中排除：{', '.join(excluded)}")

    return CustomRouteResponse(
        days=days,
        warnings=warnings,
        total_travel_minutes=result["total_minutes"],
        excluded_attraction_ids=excluded,
    )
