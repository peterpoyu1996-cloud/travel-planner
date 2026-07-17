# 知識庫欄位定義

對應 [PRD.md](../docs/PRD.md) 第6節 A–F 類。每筆景點/飯店/餐廳資料為以下 JSON 結構。

```jsonc
{
  "id": "string，唯一識別碼，例：kouri-tower",
  "name": "string，中文名稱",
  "name_local": "string，日文原名",
  "category": "attraction | hotel | restaurant",
  "region_group": "北部 | 中部 | 南部（沖繩本島標準三分法，供地理動線分群/篩選用，見下方緯度分界）",
  "sub_area": "string | null，更細的地標區域，例：美國村 / 瀨長島 / 國際通周邊，不影響篩選，只是額外描述",

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

## region_group 分界（緯度，沖繩本島）

三分法邊界跟 `scraper/merge_osm.py`／`scraper/ingest_osm.py` 用的是同一組，改一邊要記得改另一邊：

| region_group | 緯度範圍 | 大致對應 |
|---|---|---|
| 北部 | lat ≥ 26.45 | 名護、本部、國頭、古宇利島 |
| 中部 | 26.25 ≤ lat < 26.45 | 沖繩市、北谷（美國村）、讀谷、嘉手納 |
| 南部 | lat < 26.25 | 那霸、瀨長島、系滿、南城 |

只檢查緯度（南北軸），沖繩本島狹長，緯度已足夠區分；資料沒有 lat 時無法自動分類，需人工標註。

## 資料現況

- `attractions.json` / `hotels.json` / `restaurants.json` 有兩種來源：
  - `source: "excel_seed"`：使用者 2024/1/7–1/11 沖繩行程 Excel 轉錄的種子資料，核心欄位（MapCode/停車/備案）最完整，但只有 15 筆
  - `source: "osm"`：`scraper/ingest_osm.py` 從 OpenStreetMap 開放資料匯入，補廣度，但只有基本欄位（名稱/座標/分類/部分營業時間），MapCode/停車/親子適合度等核心決策欄位是 `null`，需要之後人工或 LLM 補標註
- `lat`/`lng`/`rating` 等欄位沒有來源就標 `null`，待後續跑 geocoding 或官網查證再補，**不可用猜測值填入**
- 原始 Excel 檔案是個人行程資料，**刻意不進版控**（見 `.gitignore` 的 `*.xlsx`），只有轉錄、去識別化後的 JSON 才進 repo
- 下一步：針對 `source: "osm"` 的資料，優先幫熱門項目補 MapCode 與親子/預算標籤（`scraper/enrich_llm.py`）

## name 欄位繁體中文化現況

`scraper/convert_traditional.py`（機械式新字體→繁體字元替換，零風險）+ `scraper/translate_names.py`
（LLM 輔助翻譯，只翻有把握的知名連鎖店/地標）處理過 150 筆 OSM 資料，現況：

- 45 筆本來就是純漢字、字元剛好跟繁體中文相同，不用改
- 46 筆已轉換/翻譯成繁體中文（含機械轉換、LLM翻譯、OSM社群提供的 `name:zh`/`name:zh-Hant` 標籤）
- 59 筆含假名（片假名/平假名），沒有把握正確翻譯，**刻意保留日文原名**（`name` 等於 `name_local`），
  這是刻意的取捨，避免翻錯誤導使用者，不是漏做

⚠️ **踩過的坑**：OSM 社群提供的 `name:zh`/`name:zh-Hant` 標籤不是自動信任的來源，發現過至少 2 筆
明顯的形近字誤植（例如「岸本食堂」被標成「案本食堂」、「花笠食堂」被標成「花苙」）。已人工訂正這兩筆，
但沒有逐筆全部覆核，之後若要大量信任 OSM 的中文標籤，建議先抽樣驗證。
