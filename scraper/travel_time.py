"""結合平面道路（haversine 直線距離 * 繞路係數）跟高速公路（圖論最短路徑）
兩種路線，估算兩點間車程時間，取比較快的那個。

這是估算，不是真實路況（不含車流、紅綠燈、匝道匯入時間），但比純直線距離
haversine 準，尤其是北部⇄南部這種本來就會走高速公路的長途移動。

速度假設（使用者指定）：高速公路 90km/h，平面道路 40-50km/h（用 45 當中間值）。
繞路係數 1.3：平面道路不會是直線，用個粗略係數修正haversine低估的部分。
"""

from geo_utils import haversine_km
from highway_routing import highway_distance_km

HIGHWAY_SPEED_KMH = 90
SURFACE_SPEED_KMH = 45
SURFACE_DETOUR_FACTOR = 1.3  # 平面道路不是直線，haversine要乘一個係數修正
IC_ACCESS_DETOUR_FACTOR = 1.15  # 到交流道的路通常比市區道路直一點，係數小一些


def _surface_minutes(distance_km: float, detour: float = SURFACE_DETOUR_FACTOR) -> float:
    return distance_km * detour / SURFACE_SPEED_KMH * 60


def estimate_minutes(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
    interchanges: list[dict],
    graph: dict,
) -> dict:
    """回傳 {"minutes": float, "via": "surface"|"highway", "detail": str}"""

    direct_km = haversine_km(origin_lat, origin_lon, dest_lat, dest_lon)
    direct_minutes = _surface_minutes(direct_km)

    best_highway_minutes = None
    best_highway_detail = None

    # 試離起點/終點最近的3個交流道各種組合，不是只試最近的一個——因為個別交流道
    # 之間偶爾在OSM資料裡沒連通（例如支線道路跟主線的連接路段沒被查詢到），
    # 只試最近的話遇到這種情況會整個回報「查不到高速公路路線」，試多幾個更穩
    CANDIDATES = 5
    entry_candidates = sorted(interchanges, key=lambda ic: haversine_km(origin_lat, origin_lon, ic["lat"], ic["lng"]))[:CANDIDATES]
    exit_candidates = sorted(interchanges, key=lambda ic: haversine_km(dest_lat, dest_lon, ic["lat"], ic["lng"]))[:CANDIDATES]

    for entry_ic in entry_candidates:
        for exit_ic in exit_candidates:
            if entry_ic["name"] == exit_ic["name"]:
                continue
            highway_km = highway_distance_km(entry_ic, exit_ic, graph)
            if highway_km is None:
                continue

            access_km = haversine_km(origin_lat, origin_lon, entry_ic["lat"], entry_ic["lng"])
            egress_km = haversine_km(dest_lat, dest_lon, exit_ic["lat"], exit_ic["lng"])
            minutes = (
                _surface_minutes(access_km, IC_ACCESS_DETOUR_FACTOR)
                + highway_km / HIGHWAY_SPEED_KMH * 60
                + _surface_minutes(egress_km, IC_ACCESS_DETOUR_FACTOR)
            )
            if best_highway_minutes is None or minutes < best_highway_minutes:
                best_highway_minutes = minutes
                best_highway_detail = f"經{entry_ic['name']}上、{exit_ic['name']}下，高速公路段{highway_km:.1f}km"

    if best_highway_minutes is not None and best_highway_minutes < direct_minutes:
        return {"minutes": round(best_highway_minutes, 1), "via": "highway", "detail": best_highway_detail}

    return {
        "minutes": round(direct_minutes, 1),
        "via": "surface",
        "detail": f"平面道路直線距離約{direct_km:.1f}km（含繞路係數）",
    }
