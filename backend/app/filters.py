"""規則式候選景點過濾（取代向量 RAG，見 docs/ARCHITECTURE.md 第1節）。

目的：在丟給 LLM 之前，先把 80-150 筆知識庫縮小到 10-15 筆候選，
      確保 prompt 精簡、成本可控，也讓篩選邏輯本身可測試、可除錯。
"""

import json
from pathlib import Path

from .models import TripConditions

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

BUDGET_ORDER = {"$": 1, "$$": 2, "$$$": 3}


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
        # 沒租車就排除「需要開車」的景點——注意 has_parking 跟這件事無關
        # （有沒有停車場不代表沒車去得了），之前誤把兩者混在一起判斷過
        return False

    return True


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

    return candidates[:limit]
