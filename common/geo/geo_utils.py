"""共用的地理距離工具。直線距離（haversine），不是實際路況時間，
但零成本、不用外部服務，拿來做「這兩個點大概近不近」的粗估很夠用。

放在 common/ 而不是 scraper/ 或 backend/app/，因為兩邊都要用：scraper 拿來做
離線分析/畫圖，backend 拿來在行程生成時算真實車程（見 backend/app/itinerary.py）。
"""

import math

EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def nearest(lat: float, lon: float, candidates: list[dict], lat_key: str = "lat", lon_key: str = "lon") -> tuple[dict, float] | None:
    """從 candidates（每筆要有 lat_key/lon_key）裡找離 (lat, lon) 最近的一筆，回傳 (該筆, 距離km)。"""
    best = None
    best_dist = float("inf")
    for c in candidates:
        if c.get(lat_key) is None or c.get(lon_key) is None:
            continue
        dist = haversine_km(lat, lon, c[lat_key], c[lon_key])
        if dist < best_dist:
            best, best_dist = c, dist
    return (best, best_dist) if best else None
