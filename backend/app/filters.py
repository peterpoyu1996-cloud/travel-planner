"""規則式候選景點過濾（取代向量 RAG，見 docs/ARCHITECTURE.md 第1節）。

目的：在丟給 LLM 之前，先把 190+ 筆知識庫縮小到 10-15 筆候選，
      確保 prompt 精簡、成本可控，也讓篩選邏輯本身可測試、可除錯。
"""

import json
from pathlib import Path

from .models import TripConditions

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

BUDGET_ORDER = {"$": 1, "$$": 2, "$$$": 3}

# 資料完整度排序：excel_seed/official_site 有查證過的核心欄位（MapCode/停車/親子適合度），
# osm 大多只有名稱座標。同分類內優先給 LLM 看資料比較完整的那些。
SOURCE_PRIORITY = {"excel_seed": 0, "official_site": 1, "llm_enriched": 2, "osm": 3}


def load_knowledge_base() -> list[dict]:
    entries: list[dict] = []
    for filename in ("attractions.json", "hotels.json", "restaurants.json"):
        path = DATA_DIR / filename
        if path.exists():
            entries.extend(json.loads(path.read_text(encoding="utf-8")))
    return entries


def matches_conditions(entry: dict, conditions: TripConditions) -> bool:
    if conditions.has_kids and entry.get("kid_friendly") is False:
        return False

    if entry.get("budget_level") and conditions.budget_level:
        if BUDGET_ORDER.get(entry["budget_level"], 99) > BUDGET_ORDER.get(conditions.budget_level, 99):
            return False

    if not conditions.has_car and entry.get("travel_mode") == "開車":
        # 沒租車就排除「需要開車」的景點——但如果這筆資料離單軌電車站走路範圍內
        # （nearest_monorail_station 有值，見 scraper/tag_transit_access.py），
        # 就算 travel_mode 標記開車（反映的是原始資料來源當初怎麼去的），
        # 沒車的人還是有機會走路/單軌到，不用排除
        if not entry.get("nearest_monorail_station"):
            return False

    return True


def _balanced_by_category(candidates: list[dict], limit: int) -> list[dict]:
    """跨分類輪流挑，不能讓某個分類資料量大就把整個 limit 佔滿——
    這是真的踩過的雷：attractions.json 擴充到 92 筆後，原本單純 [:limit] 的做法
    會讓候選清單裡完全沒有飯店/餐廳（都還沒排到就被切掉了），行程生成因此
    生不出住宿/用餐建議。改成每個分類各自排隊（按 SOURCE_PRIORITY 排序過），
    輪流各拿一筆，直到湊滿 limit 或所有分類都拿完。
    """
    by_category: dict[str, list[dict]] = {}
    for entry in candidates:
        by_category.setdefault(entry.get("category", ""), []).append(entry)

    for group in by_category.values():
        group.sort(key=lambda e: SOURCE_PRIORITY.get(e.get("source"), 99))

    queues = list(by_category.values())
    result: list[dict] = []
    while queues and len(result) < limit:
        next_queues = []
        for queue in queues:
            if len(result) >= limit:
                break
            result.append(queue.pop(0))
            if queue:
                next_queues.append(queue)
        queues = next_queues

    return result


def select_candidates(
    conditions: TripConditions,
    category: str | None = None,
    region_group: str | None = None,
    limit: int = 15,
) -> list[dict]:
    kb = load_knowledge_base()

    candidates = [e for e in kb if matches_conditions(e, conditions)]

    if category:
        candidates = [e for e in candidates if e.get("category") == category]
    if region_group:
        candidates = [e for e in candidates if e.get("region_group") == region_group]

    if category:
        # 已經指定單一分類了，不需要再跨分類平衡
        candidates.sort(key=lambda e: SOURCE_PRIORITY.get(e.get("source"), 99))
        return candidates[:limit]

    return _balanced_by_category(candidates, limit)
