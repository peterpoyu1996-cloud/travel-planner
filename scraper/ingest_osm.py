"""把 data/raw/osm_okinawa_*.json（osm_overpass.py 抓回來的原始資料）
篩選、去重後，正式匯入成 data/*.json 的新條目（source="osm"），補足廣度。

跟 merge_osm.py 的差異：merge_osm.py 是「幫既有的 15 筆種子資料補座標」，
這支是「從 OSM 開放資料新增全新的條目」，解決知識庫筆數太少的問題。

已知限制（誠實寫在這裡，不是藏起來）：
- OSM 大多沒有中文名稱，沒有的話 `name` 會直接用日文原名，不會亂猜翻譯
- `travel_mode`／`has_parking`／MapCode／親子適合度等核心決策欄位一律是 null，
  之後要嘛人工補、要嘛跑 scraper/enrich_llm.py 讓 LLM 幫忙推論
- 餐廳原始資料有 1372 筆太多，用「OSM 標籤完整度」當簡單品質分數取前 N 筆，
  不是真的知道哪家比較好吃
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"

# region_group 緯度分界，跟 data/schema.md、merge_osm.py 保持一致
def region_group_from_lat(lat: float) -> str:
    if lat >= 26.45:
        return "北部"
    if lat >= 26.25:
        return "中部"
    return "南部"


CATEGORY_CONFIG = {
    "attraction": {
        "seed_file": "attractions.json",
        "osm_file": "osm_okinawa_attractions.json",
        "id_prefix": "osm-attr",
        "cap": 60,
        "stored_category": "attraction",
    },
    "hotel": {
        "seed_file": "hotels.json",
        "osm_file": "osm_okinawa_hotels.json",
        "id_prefix": "osm-hotel",
        "cap": 30,
        "stored_category": "hotel",
    },
    "restaurant": {
        "seed_file": "restaurants.json",
        "osm_file": "osm_okinawa_restaurants.json",
        "id_prefix": "osm-rest",
        "cap": 60,
        "stored_category": "restaurant",
    },
    # 海灘不是獨立的 schema 分類，併入 attractions.json，category 仍存 "attraction"，
    # 用 id 前綴 osm-beach 跟 indoor_outdoor="戶外" 區分
    "beach": {
        "seed_file": "attractions.json",
        "osm_file": "osm_okinawa_beaches.json",
        "id_prefix": "osm-beach",
        "cap": 25,
        "stored_category": "attraction",
    },
}

# 少數信心足夠的分類線索才推 indoor_outdoor，其餘一律 null
INDOOR_OUTDOOR_HINTS = {
    "museum": "室內",
    "aquarium": "室內",
    "beach_resort": "戶外",
    "viewpoint": "戶外",
    "zoo": "兩者皆有",
    "theme_park": "戶外",
}


def normalize(s: str) -> str:
    return s.replace(" ", "").replace("　", "").lower()


def is_duplicate(name: str, name_local: str, existing_names: set[str]) -> bool:
    """雙向子字串比對，不是精確相等——OSM 常常只有店名的一部分
    （例如「大家」對到既有種子資料的「百年古家 大家」），精確比對會漏掉。"""
    candidates = [normalize(name), normalize(name_local)]
    for candidate in candidates:
        if not candidate:
            continue
        for existing in existing_names:
            if candidate in existing or existing in candidate:
                return True
    return False


def quality_score(tags: dict) -> int:
    keys = ("opening_hours", "cuisine", "phone", "contact:phone", "website", "contact:website")
    addr = 1 if any(k.startswith("addr:") for k in tags) else 0
    return sum(1 for k in keys if tags.get(k)) + addr


def build_address(tags: dict) -> str | None:
    if tags.get("addr:full"):
        return tags["addr:full"]
    parts = [tags.get("addr:city"), tags.get("addr:street"), tags.get("addr:housenumber")]
    parts = [p for p in parts if p]
    return "".join(parts) if parts else None


def to_entry(category: str, el: dict, id_prefix: str) -> dict | None:
    tags = el.get("tags", {})
    lat, lon = el.get("lat"), el.get("lon")
    if lat is None or lon is None:
        # way/relation 用 "out center;" 查詢時，座標會在 center 裡而不是頂層
        center = el.get("center") or {}
        lat, lon = center.get("lat"), center.get("lon")
    if lat is None or lon is None:
        return None

    name_local = tags.get("name")
    if not name_local:
        return None

    name = tags.get("name:zh-Hant") or tags.get("name:zh") or name_local

    indoor_outdoor = None
    for key in ("tourism", "leisure", "amenity"):
        hint = INDOOR_OUTDOOR_HINTS.get(tags.get(key))
        if hint:
            indoor_outdoor = hint
            break
    if tags.get("natural") == "beach":
        indoor_outdoor = "戶外"

    return {
        "id": f"{id_prefix}-{el['id']}",
        "name": name,
        "name_local": name_local,
        "category": category,
        "region_group": region_group_from_lat(lat),
        "sub_area": tags.get("addr:suburb"),
        "address": build_address(tags),
        "lat": lat,
        "lng": lon,
        "opening_hours": tags.get("opening_hours"),
        "phone": tags.get("phone") or tags.get("contact:phone"),
        "website": tags.get("website") or tags.get("contact:website"),
        "rating": None,
        "travel_time_from_prev": None,
        "travel_mode": None,
        "mapcode": None,
        "suggested_stay_duration": None,
        "has_parking": None,
        "parking_name": None,
        "parking_mapcode": None,
        "parking_notes": None,
        "is_flexible_slot": False,
        "conditional_note": None,
        "requires_reservation": False,
        "backup_option": None,
        "kid_friendly": None,
        "kid_age_notes": None,
        "indoor_outdoor": indoor_outdoor,
        "budget_level": None,
        "description_for_embedding": None,
        "source": "osm",
        "source_note": f"OSM匯入（node {el['id']}），travel_mode/停車/親子適合度等待補充",
    }


def ingest_category(category: str) -> None:
    config = CATEGORY_CONFIG[category]
    seed_path = DATA_DIR / config["seed_file"]
    osm_path = RAW_DIR / config["osm_file"]

    existing = json.loads(seed_path.read_text(encoding="utf-8")) if seed_path.exists() else []
    existing_ids = {e["id"] for e in existing}
    existing_names = {normalize(e["name_local"]) for e in existing if e.get("name_local")}
    existing_names |= {normalize(e["name"]) for e in existing if e.get("name")}

    if not osm_path.exists():
        print(f"[ingest_osm] 找不到 {osm_path}，略過 {category}（請先跑 osm_overpass.py）")
        return

    raw = json.loads(osm_path.read_text(encoding="utf-8"))
    elements = raw.get("elements", [])

    candidates = []
    for el in elements:
        entry = to_entry(config["stored_category"], el, config["id_prefix"])
        if entry is None:
            continue
        if entry["id"] in existing_ids:
            continue
        if is_duplicate(entry["name"], entry["name_local"], existing_names):
            continue  # 已經有種子資料涵蓋（含子字串包含的情況），避免重複
        candidates.append((quality_score(el.get("tags", {})), entry))

    candidates.sort(key=lambda pair: pair[0], reverse=True)
    accepted = []
    for _, entry in candidates:
        if len(accepted) >= config["cap"]:
            break
        if is_duplicate(entry["name"], entry["name_local"], existing_names):
            continue  # 候選之間彼此也可能重複（同店多筆 OSM node），一併擋掉
        accepted.append(entry)
        existing_names.add(normalize(entry["name_local"]))
        existing_names.add(normalize(entry["name"]))

    merged = existing + accepted
    seed_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

    by_region = {"北部": 0, "中部": 0, "南部": 0}
    for e in accepted:
        by_region[e["region_group"]] += 1

    print(
        f"[ingest_osm] {category}: 原有 {len(existing)} 筆 + 新增 {len(accepted)} 筆"
        f"（北部{by_region['北部']}/中部{by_region['中部']}/南部{by_region['南部']}）"
        f" = {len(merged)} 筆，寫回 {seed_path}"
    )


def main() -> None:
    for category in CATEGORY_CONFIG:
        ingest_category(category)


if __name__ == "__main__":
    main()
