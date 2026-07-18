"""幫每筆知識庫資料標註「離最近的單軌電車站多遠」，解決「不開車行程」缺乏
大眾運輸資訊的問題（見 docs/ROADMAP.md 的不開車行程評估）。

只處理單軌電車（沖繩本島唯一的軌道系統，涵蓋那霸市區到浦添一帶），
北部/中部大部分景點本來就離單軌很遠，會誠實標成 null，不是漏標。

新增兩個欄位：
- nearest_monorail_station：最近站名，超過 WALKABLE_KM 就是 null（代表「不是走路可達」，
  不代表完全去不了，只是這支腳本沒有巴士資料可以判斷）
- monorail_distance_km：到最近站的直線距離（haversine，不是實際步行路徑），僅供參考
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.geo.geo_utils import nearest

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
STATIONS_PATH = DATA_DIR / "transit_stations.json"

WALKABLE_KM = 1.2  # 大約步行15分鐘的直線距離，抓寬鬆一點因為haversine比實際路徑短


def tag_file(filename: str, stations: list[dict]) -> int:
    path = DATA_DIR / filename
    entries = json.loads(path.read_text(encoding="utf-8"))

    tagged = 0
    for entry in entries:
        if entry.get("lat") is None or entry.get("lng") is None:
            entry["nearest_monorail_station"] = None
            entry["monorail_distance_km"] = None
            continue

        result = nearest(entry["lat"], entry["lng"], stations, lat_key="lat", lon_key="lng")
        if result is None:
            entry["nearest_monorail_station"] = None
            entry["monorail_distance_km"] = None
            continue

        station, dist_km = result
        entry["monorail_distance_km"] = round(dist_km, 2)
        if dist_km <= WALKABLE_KM:
            entry["nearest_monorail_station"] = station["name"]
            tagged += 1
        else:
            entry["nearest_monorail_station"] = None

    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    return tagged


def main() -> None:
    stations = json.loads(STATIONS_PATH.read_text(encoding="utf-8"))
    for filename in ("attractions.json", "hotels.json", "restaurants.json"):
        tagged = tag_file(filename, stations)
        print(f"[tag_transit_access] {filename}: {tagged} 筆在單軌站 {WALKABLE_KM}km 步行範圍內")


if __name__ == "__main__":
    main()
