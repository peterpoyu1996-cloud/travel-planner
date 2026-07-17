# 知識庫欄位定義

對應 [PRD.md](../docs/PRD.md) 第6節 A–F 類。每筆景點/飯店/餐廳資料為以下 JSON 結構。

```jsonc
{
  "id": "string，唯一識別碼，例：kouri-tower",
  "name": "string，中文名稱",
  "name_local": "string，日文原名",
  "category": "attraction | hotel | restaurant",
  "region_group": "string，地理分群，例：那霸市區 / 中部 / 北部（供地理動線分群用）",

  // A. 基本資訊
  "address": "string | null",
  "lat": "number | null",
  "lng": "number | null",
  "opening_hours": "string | null",
  "phone": "string | null",
  "website": "string | null",
  "rating": "number | null",

  // B. 動線與交通
  "travel_time_from_prev": "string | null，例：約1小時 / 30分鐘車程",
  "travel_mode": "開車 | 步行 | 大眾運輸 | null",
  "mapcode": "string | null，日本車用導航 MapCode",
  "suggested_stay_duration": "string | null",

  // C. 停車
  "has_parking": "boolean",
  "parking_name": "string | null",
  "parking_mapcode": "string | null",
  "parking_notes": "string | null",

  // D. 備案與彈性設計
  "is_flexible_slot": "boolean",
  "conditional_note": "string | null",
  "requires_reservation": "boolean",
  "backup_option": "string | null，可填其他 id",

  // E. 決策相關標籤
  "kid_friendly": "boolean | null",
  "kid_age_notes": "string | null",
  "indoor_outdoor": "室內 | 戶外 | 兩者皆有 | null",
  "budget_level": "$ | $$ | $$$ | null",

  // F. 向量化描述
  "description_for_embedding": "string | null",

  // 資料來源追溯
  "source": "excel_seed | osm | official_site | llm_enriched",
  "source_note": "string | null"
}
```

## 資料現況

- `attractions.json` / `hotels.json` / `restaurants.json` 目前只有從使用者 2024/1/7–1/11 沖繩行程 Excel 轉錄的種子資料（`source: "excel_seed"`）
- `lat`/`lng`/`rating` 等欄位 Excel 沒有提供，先標 `null`，待後續跑 geocoding 或官網查證再補，**不可用猜測值填入**
- 下一步：`scraper/sources/osm_overpass.py` 補齊經緯度與更多景點廣度
