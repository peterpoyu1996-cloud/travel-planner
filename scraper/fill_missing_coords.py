"""補齊知識庫裡「現在確實 lat/lng 是 null」的紀錄，不重新比對整批資料。

跟 merge_osm.py 的差異：merge_osm.py 是「拿新抓的 OSM 原始資料重新比對整批種子資料」，
用在資料管線早期、種子資料還沒被其他來源（official_site/llm_enriched）補過的階段——
如果現在拿它對現有 KB 整批重跑，任何在目前 data/raw/ OSM 快照裡找不到的既有好資料
都會被覆蓋成 null（見 merge_osm.py 第121-122行的 else 分支），會把已經查證過的資料洗掉。

這支只處理「lat/lng 現在確實是 null」的那幾筆，找到才寫，找不到維持原樣、不動任何
已經有座標的紀錄，也不覆寫 source 欄位（那描述整筆記錄的主要來源），只在 source_note
附加座標查證方式，比照 data/schema.md 裡「多段來源備註用分號串接」的既有慣例。

比對來源，依序嘗試（都是 🟢A 級開放資料，見 CLAUDE.md 爬蟲合規分級）：
1. data/raw/osm_okinawa_*.json（Overpass 批次快照，重用 merge_osm.py 的名稱比對 +
   region_group 地理合理性檢查邏輯，避免連鎖店配到錯分店）
2. 上面沒找到的話，改打 Nominatim 即時查（能查到 Overpass tourism/amenity tag
   沒收錄、但 Nominatim 索引到的個別店家/飯店），一樣套同一組地理合理性檢查；
   有 address 欄位的優先用地址查（比店名查更精準），沒有才退回用 name_local 查
   （加「沖縄」當地區提示，避免配到日本本土同名地點）
"""

import json
import sys
import time
from pathlib import Path

import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from merge_osm import find_match, in_region, load_osm_elements  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "travel-planner-okinawa-mvp/0.1 (personal portfolio project)"
NOMINATIM_DELAY_SEC = 1.1  # Nominatim usage政策：單一來源最多1req/秒，抓寬一點margin

CATEGORY_FILES = {
    "attraction": "attractions.json",
    "restaurant": "restaurants.json",
    "hotel": "hotels.json",
}
CATEGORY_TO_OSM_ELEMENTS_KEY = {
    "attraction": "attraction",
    "restaurant": "restaurant",
    "hotel": "hotel",
}


def nominatim_search(query: str) -> list[dict]:
    resp = requests.get(
        NOMINATIM_URL,
        params={"q": query, "format": "json", "limit": 5, "countrycodes": "jp"},
        headers={"User-Agent": USER_AGENT},
        timeout=20,
    )
    resp.raise_for_status()
    time.sleep(NOMINATIM_DELAY_SEC)
    return resp.json()


def try_nominatim(entry: dict) -> tuple[float, float, str] | None:
    """回傳 (lat, lng, 查證方式描述) 或 None。有 address 優先用地址查，
    找不到才退回用 name_local + 沖縄 查，兩種查法都套 region_group 地理合理性檢查。
    """
    region_group = entry.get("region_group", "")
    candidates_tried = []

    if entry.get("address"):
        candidates_tried.append(("地址", entry["address"]))
    if entry.get("name_local"):
        candidates_tried.append(("店名", f"{entry['name_local']} 沖縄"))

    for method, query in candidates_tried:
        try:
            results = nominatim_search(query)
        except requests.RequestException as e:
            print(f"[fill_missing_coords]   Nominatim 查詢失敗（{method}: {query!r}）：{e}")
            continue

        for r in results:
            lat = float(r["lat"])
            if not in_region(lat, region_group):
                continue
            return lat, float(r["lon"]), f"Nominatim（{method}查詢：{query}）"

        if results:
            print(f"[fill_missing_coords]   {method}查詢有 {len(results)} 個結果，但都不在「{region_group}」合理緯度範圍內，捨棄避免誤配")

    return None


def fill_category(category: str) -> tuple[int, int]:
    path = DATA_DIR / CATEGORY_FILES[category]
    entries = json.loads(path.read_text(encoding="utf-8"))
    osm_elements = load_osm_elements(category)

    filled, still_missing = 0, 0
    changed = False

    for entry in entries:
        if entry.get("lat") is not None and entry.get("lng") is not None:
            continue  # 已經有座標，完全不動

        print(f"[fill_missing_coords] 處理 {entry['id']}（{entry.get('name_local')}，{entry.get('region_group')}）")

        # 1. 先試本地 OSM 快照（不用打網路，也是 merge_osm.py 同一套比對邏輯）
        match = None
        if entry.get("name_local"):
            match = find_match(entry["name_local"], osm_elements, entry.get("region_group", ""))

        if match:
            lat, lng = match.get("lat"), match.get("lon")
            method = f"OSM快照比對: {match.get('tags', {}).get('name', '')}"
        else:
            # 2. 本地快照沒有，改打 Nominatim 即時查
            found = try_nominatim(entry)
            if found:
                lat, lng, method = found
            else:
                lat = lng = method = None

        if lat is not None and lng is not None:
            entry["lat"] = lat
            entry["lng"] = lng
            base_note = (entry.get("source_note") or "").rstrip("；")
            entry["source_note"] = f"{base_note}；lat/lng 由 {method} 補齊" if base_note else f"lat/lng 由 {method} 補齊"
            filled += 1
            changed = True
            print(f"[fill_missing_coords]   -> 補上 ({lat}, {lng})，來源：{method}")
        else:
            still_missing += 1
            print(f"[fill_missing_coords]   -> 找不到可信候選，維持 null")

    if changed:
        path.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[fill_missing_coords] {category}: 補上 {filled} 筆，仍缺 {still_missing} 筆，已寫回 {path}")
    else:
        print(f"[fill_missing_coords] {category}: 沒有需要補的紀錄")

    return filled, still_missing


def main() -> None:
    total_filled, total_missing = 0, 0
    for category in CATEGORY_FILES:
        filled, missing = fill_category(category)
        total_filled += filled
        total_missing += missing
    print(f"\n[fill_missing_coords] 總計：補上 {total_filled} 筆，仍缺 {total_missing} 筆（維持 null，不猜測）")


if __name__ == "__main__":
    main()
