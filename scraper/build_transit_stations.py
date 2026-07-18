"""把 osm_overpass.py 抓到的 railway=station 原始資料整理成 data/transit_stations.json。
沖繩本島只有一條鐵路系統（沖縄都市モノレール／ゆいレール），所以查詢範圍內的
railway=station 節點就是全部19個單軌電車站，不需要額外篩選。
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_PATH = DATA_DIR / "raw" / "osm_okinawa_transit_stations.json"
OUT_PATH = DATA_DIR / "transit_stations.json"


def main() -> None:
    raw = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    stations = []
    for el in raw.get("elements", []):
        tags = el.get("tags", {})
        stations.append({
            "id": f"monorail-{el['id']}",
            "name": tags.get("name"),
            "name_en": tags.get("name:en"),
            "lat": el.get("lat"),
            "lng": el.get("lon"),
            "line": "沖縄都市モノレール（ゆいレール）",
            "source": "osm",
        })

    stations.sort(key=lambda s: s["lat"])
    OUT_PATH.write_text(json.dumps(stations, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[build_transit_stations] 寫入 {len(stations)} 個站點到 {OUT_PATH}")


if __name__ == "__main__":
    main()
