"""A 級來源：OpenStreetMap Overpass API。
開放資料（ODbL），官方允許程式化擷取，不是「爬蟲」意義上的規避行為。
用途：補齊景點/餐廳/飯店的座標、分類、部分營業時間，作為「廣度資料」。
使用規範：https://wiki.openstreetmap.org/wiki/Overpass_API#Rules_of_usage
（單一 IP 不要並行多個請求、避免過於頻繁）
"""

import json
import sys
import time
from pathlib import Path

import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "travel-planner-okinawa-mvp/0.1 (personal portfolio project)"

# 沖繩本島大致範圍（south, west, north, east），不含離島
OKINAWA_MAIN_ISLAND_BBOX = (26.0, 127.6, 26.9, 128.3)

QUERY_TEMPLATES = {
    "attractions": """
        [out:json][timeout:60];
        (
          node["tourism"~"attraction|museum|aquarium|zoo|theme_park|viewpoint"]({bbox});
          node["leisure"~"park|beach_resort"]({bbox});
        );
        out body;
    """,
    "restaurants": """
        [out:json][timeout:60];
        (
          node["amenity"~"restaurant|cafe"]({bbox});
        );
        out body;
    """,
    "hotels": """
        [out:json][timeout:60];
        (
          node["tourism"~"hotel|guest_house|apartment"]({bbox});
        );
        out body;
    """,
}


def fetch(category: str, bbox: tuple[float, float, float, float] = OKINAWA_MAIN_ISLAND_BBOX) -> dict:
    if category not in QUERY_TEMPLATES:
        raise ValueError(f"未知分類: {category}，可用: {list(QUERY_TEMPLATES)}")

    bbox_str = ",".join(str(v) for v in bbox)
    query = QUERY_TEMPLATES[category].format(bbox=bbox_str)

    resp = requests.post(
        OVERPASS_URL,
        data={"data": query},
        headers={"User-Agent": USER_AGENT},
        timeout=90,
    )
    resp.raise_for_status()
    return resp.json()


def save_raw(category: str, payload: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"osm_okinawa_{category}.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def main() -> None:
    import sys

    only = sys.argv[1] if len(sys.argv) > 1 else None
    categories = [only] if only else list(QUERY_TEMPLATES)

    out_dir = Path(__file__).resolve().parents[2] / "data" / "raw"
    for category in categories:
        print(f"[osm_overpass] 抓取 {category} ...")
        payload = fetch(category)
        path = save_raw(category, payload, out_dir)
        n = len(payload.get("elements", []))
        print(f"[osm_overpass] {category}: {n} 筆，寫入 {path}")
        time.sleep(5)  # 尊重 Overpass 使用規範，避免連續高頻請求


if __name__ == "__main__":
    main()
