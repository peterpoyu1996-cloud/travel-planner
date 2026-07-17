"""把 OSM Overpass 抓回來的原始資料（data/raw/osm_okinawa_*.json）
比對進種子資料（data/*.json），用 name_local 做名稱比對，補上 lat/lng。

比對邏輯：
1. 名稱雙向子字串包含才算候選（避免完全不相關的亂配對）
2. 連鎖店/同名設施常有多個分店，光靠名稱比對會配到錯的分店（例如燒肉本部牧場
   在 Excel 裡是北部的店，卻可能配到那霸的分店）。所以再用 region_group 對應的
   概略緯度範圍做合理性檢查，落在範圍外的候選直接捨棄，不寧可錯殺不留錯資料
3. 找不到通過檢查的候選，維持/還原為 null，印出來人工後續確認
"""

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"

CATEGORY_TO_SEED_FILE = {
    "attraction": "attractions.json",
    "restaurant": "restaurants.json",
    "hotel": "hotels.json",
}
CATEGORY_TO_OSM_FILE = {
    "attraction": "osm_okinawa_attractions.json",
    "restaurant": "osm_okinawa_restaurants.json",
    "hotel": "osm_okinawa_hotels.json",
}

# 沖繩本島大致南北分區緯度範圍，用來擋掉「同名但配到錯分店/錯地點」的誤配對
# 只檢查緯度（南北軸），沖繩本島狹長，緯度已足夠區分北中南
REGION_LAT_RANGE = {
    "那霸市區": (26.10, 26.28),
    "那霸市區（瀨長島）": (26.10, 26.25),
    "中部": (26.25, 26.48),
    "中部（美國村）": (26.25, 26.48),
    "北部": (26.45, 26.90),
}


def normalize(s: str) -> str:
    return s.replace(" ", "").replace("　", "").lower()


def load_osm_elements(category: str) -> list[dict]:
    path = RAW_DIR / CATEGORY_TO_OSM_FILE[category]
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("elements", [])


def in_region(lat: float, region_group: str) -> bool:
    bounds = REGION_LAT_RANGE.get(region_group)
    if not bounds:
        return True  # 沒定義範圍的分區不做地理檢查
    lo, hi = bounds
    return lo <= lat <= hi


def find_match(name_local: str, elements: list[dict], region_group: str) -> dict | None:
    target = normalize(name_local)
    name_candidates = []
    for el in elements:
        tags = el.get("tags", {})
        for key in ("name", "name:ja", "name:en"):
            c = tags.get(key)
            if not c:
                continue
            c_norm = normalize(c)
            if target in c_norm or c_norm in target:
                name_candidates.append(el)
                break

    # 先篩地理區域合理的候選，避免同名不同分店的誤配
    region_valid = [el for el in name_candidates if el.get("lat") is not None and in_region(el["lat"], region_group)]
    if region_valid:
        # 名稱比對長度差最小的優先（比較貼近完整店名）
        region_valid.sort(key=lambda el: abs(len(normalize(el.get("tags", {}).get("name", ""))) - len(target)))
        return region_valid[0]

    if name_candidates:
        print(f"[merge_osm]   （有 {len(name_candidates)} 個同名候選，但都不在 {region_group} 合理緯度範圍內，捨棄避免誤配）")
    return None


def strip_previous_osm_note(source_note: str | None) -> str:
    if not source_note:
        return ""
    return re.sub(r"\s*\|\s*OSM比對:.*$", "", source_note)


def merge_category(category: str) -> None:
    seed_path = DATA_DIR / CATEGORY_TO_SEED_FILE[category]
    entries = json.loads(seed_path.read_text(encoding="utf-8"))
    elements = load_osm_elements(category)

    matched, unmatched = 0, 0
    for entry in entries:
        name_local = entry.get("name_local")
        if not name_local:
            unmatched += 1
            continue

        base_note = strip_previous_osm_note(entry.get("source_note"))
        match = find_match(name_local, elements, entry.get("region_group", ""))

        if match:
            entry["lat"] = match.get("lat")
            entry["lng"] = match.get("lon")
            osm_name = match.get("tags", {}).get("name", "")
            entry["source_note"] = f"{base_note} | OSM比對: {osm_name}".strip(" |")
            if not entry.get("address") and match.get("tags", {}).get("addr:full"):
                entry["address"] = match["tags"]["addr:full"]
            matched += 1
            print(f"[merge_osm] 命中 {entry['id']} <- {osm_name} ({match.get('lat')}, {match.get('lon')})")
        else:
            entry["lat"] = None
            entry["lng"] = None
            entry["source_note"] = base_note or entry.get("source_note")
            unmatched += 1
            print(f"[merge_osm] 未命中/已捨棄誤配，維持 null: {entry['id']} ({name_local})")

    seed_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[merge_osm] {category}: 命中 {matched}，未命中 {unmatched}，已寫回 {seed_path}")


def main() -> None:
    for category in CATEGORY_TO_SEED_FILE:
        merge_category(category)


if __name__ == "__main__":
    main()
