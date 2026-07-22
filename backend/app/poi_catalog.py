"""GET /attractions 用的裁剪過公開清單，給前端自訂路線的景點選單用。

不是直接把 filters.load_knowledge_base() 的完整紀錄丟出去：source_note 常是寫給
未來維護者看的內部 QA 備註（例如查證推理過程），description_for_embedding 是
已放棄的向量 RAG 路徑遺留欄位（見 docs/ARCHITECTURE.md），這些都不適合原樣
暴露成公開 API 回應，會把整個內部 schema 變成事實上的公開 API 合約。

recommendation_score 從一開始故意不開放（見 CHANGELOG/討論紀錄：這欄位當時還沒
大量驗證過），這次應使用者要求開放——查詢頁需要靠它排序/篩選景點，跟 kid_friendly
同樣是 0-5 星等（0.1級距），資料完整度目前約 80%。
"""

from pydantic import BaseModel

from .filters import load_knowledge_base


class PublicPOI(BaseModel):
    id: str
    name: str
    category: str
    region_group: str | None = None
    sub_area: str | None = None
    lat: float | None = None
    lng: float | None = None
    suggested_stay_duration: str | None = None
    kid_friendly: float | None = None
    recommendation_score: float | None = None
    budget_level: str | None = None


def list_public_pois() -> list[PublicPOI]:
    entries = load_knowledge_base()
    return [
        PublicPOI(
            id=entry["id"],
            # translated_name 保證是中文，name 沒把握翻譯正確時會是日文原文
            # （跟 backend/app/itinerary.py 的 SYSTEM_PROMPT 規則 5 一致）
            name=entry.get("translated_name") or entry.get("name") or entry.get("name_local", ""),
            category=entry.get("category", ""),
            region_group=entry.get("region_group"),
            sub_area=entry.get("sub_area"),
            lat=entry.get("lat"),
            lng=entry.get("lng"),
            suggested_stay_duration=entry.get("suggested_stay_duration"),
            kid_friendly=entry.get("kid_friendly"),
            recommendation_score=entry.get("recommendation_score"),
            budget_level=entry.get("budget_level"),
        )
        for entry in entries
    ]
