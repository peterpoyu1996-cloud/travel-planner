"""把 osm_overpass.py 抓到的高速公路（motorway/motorway_link）路段幾何
跟交流道（motorway_junction）節點，整理成 data/highway_network.json：

- segments：每段路的座標序列（畫地圖用）
- interchanges：交流道清單，同名的多個節點（進/出匝道各一個）合併成一個代表點

不在這裡算「交流道到交流道的公路距離」——那是 scraper/highway_routing.py 的事，
用圖論最短路徑動態算，理由見那支檔案的說明。這裡只負責把原始資料整理乾淨。
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"


def load_segments() -> list[dict]:
    raw = json.loads((RAW_DIR / "osm_okinawa_highway_geometry.json").read_text(encoding="utf-8"))
    segments = []
    for el in raw.get("elements", []):
        geometry = el.get("geometry")
        if not geometry:
            continue
        points = [[pt["lat"], pt["lon"]] for pt in geometry]
        if len(points) < 2:
            continue
        tags = el.get("tags", {})
        segments.append({
            "way_id": el["id"],
            "name": tags.get("name"),
            "highway": tags.get("highway"),
            "points": points,
        })
    return segments


def load_interchanges() -> list[dict]:
    raw = json.loads((RAW_DIR / "osm_okinawa_highway_junctions.json").read_text(encoding="utf-8"))

    # 同名交流道常常有多個節點（不同方向的匝道），合併成一個代表點（取平均座標）
    grouped: dict[str, list[dict]] = defaultdict(list)
    for el in raw.get("elements", []):
        name = el.get("tags", {}).get("name")
        if not name or el.get("lat") is None:
            continue
        grouped[name].append(el)

    interchanges = []
    for name, nodes in grouped.items():
        lat = sum(n["lat"] for n in nodes) / len(nodes)
        lon = sum(n["lon"] for n in nodes) / len(nodes)
        interchanges.append({
            "name": name,
            "ref": nodes[0].get("tags", {}).get("ref"),
            "lat": lat,
            "lng": lon,
            "node_count": len(nodes),
        })
    return interchanges


def main() -> None:
    segments = load_segments()
    interchanges = load_interchanges()

    out = {"segments": segments, "interchanges": interchanges}
    out_path = DATA_DIR / "highway_network.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[build_highway_network] {len(segments)} 段路線、{len(interchanges)} 個交流道（已合併同名節點），寫入 {out_path}")


if __name__ == "__main__":
    main()
