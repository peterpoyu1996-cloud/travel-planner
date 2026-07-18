# ARCHITECTURE｜旅遊決策助手（沖繩試點）v0.1

本文件彙整目前已定案的技術架構決策，作為實作依據。設計原則：**零基礎設施成本**，LLM 呼叫成本控制在可忽略範圍內。

## 1. 技術棧

| 層 | 選擇 | 理由 |
|---|---|---|
| 前端 | React + Vite + TypeScript | 純網頁 SPA，不需要 SSR/API routes（API 由 Python 後端提供），比 Next.js 輕量 |
| 後端 API | Python + FastAPI | 與爬蟲共用 Python 生態；FastAPI 內建 Pydantic 驗證，符合 PRD 的資料 schema 需求 |
| 爬蟲 | Python (requests + BeautifulSoup4) | 生態成熟；用 `urllib.robotparser` 檢查 robots.txt |
| 資料儲存 | 本地 JSON 檔案（`/data`） | 資料量 190+ 筆，不需要資料庫伺服器，免費、易版控、易人工檢視 |
| 檢索方式 | 規則式過濾（非向量 RAG） | 結構化小資料集，用標籤/地區/預算/親子條件直接過濾候選清單，交給 LLM 生成 |
| LLM | Claude API（Haiku 為主） | 篩選後僅 10–15 候選景點進 prompt，單次生成成本 < $0.01；已設定 Anthropic Console 支出上限 |

## 2. 資料夾結構

```
travel-planner/
├── docs/                    # PRD / USER_FLOW / MVP / ARCHITECTURE
├── data/                    # 知識庫本體（JSON 檔案，人工可讀可編輯）
│   ├── schema.md            # 欄位定義說明（對應 PRD 第6節 A-F 類）
│   ├── attractions.json
│   ├── hotels.json
│   └── restaurants.json
├── common/                  # backend 跟 scraper 都要用的共用 Python 套件
│   └── geo/
│       ├── geo_utils.py     # haversine 直線距離
│       ├── highway_routing.py # 高速公路網路圖 + Dijkstra 最短路徑
│       └── travel_time.py   # 平面道路 vs 高速公路，取較快者估算車程分鐘數
├── scraper/                 # Python 爬蟲（A/B 級來源）+ 資料處理批次工具
│   ├── requirements.txt
│   ├── sources/
│   │   ├── osm_overpass.py  # A級：OpenStreetMap 開放資料
│   │   └── official_sites.py# B級：官網爬取，含 robots.txt 檢查
│   ├── ingest_osm.py        # 把 OSM 原始資料匯入知識庫（含 beach 類別）
│   ├── build_highway_network.py # 整理高速公路路段+交流道
│   ├── draw_map.py          # 畫知識庫地圖（docs/assets/okinawa_knowledge_map.png）
│   └── enrich_llm.py        # 一次性批次跑 LLM 幫忙標註親子適合度等主觀欄位
├── backend/                 # FastAPI 服務
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── filters.py       # 規則式候選景點過濾邏輯（跨分類平衡＋依資料完整度排序）
│   │   └── itinerary.py     # 組 prompt、呼叫 LLM 生成行程，再用 common/geo 覆蓋真實車程
└── frontend/                # React + Vite + TS
    └── (由 `npm create vite` 產生)
```

## 3. 資料流

```
[scraper/sources/*.py] → 抓 A/B 級來源原始資料
        ↓
[data/*.json 手動合併]  ← 也合併使用者 Excel 種子資料（MapCode/停車/備案等核心欄位）
        ↓
[scraper/enrich_llm.py] → 一次性批次呼叫 LLM，補上親子適合度/雨天可用性等主觀標籤，寫回 JSON（快取，不重複呼叫）
        ↓
[backend/app/filters.py] → 使用者送出條件 → 規則式過濾出候選清單（跨分類平衡，避免某分類資料量大就佔滿整個候選清單）
        ↓
[backend/app/itinerary.py] → 候選清單 + 使用者條件 → 組 prompt → 透過 LLMProvider 生成逐日行程
        ↓
[common/geo/travel_time.py] → 用候選資料的真實座標，重新算每天相鄰站點的車程，覆蓋掉 LLM 填的
        （LLM 負責「排哪些站、為什麼」，車程數字交給算的，不讓模型亂猜距離）
        ↓
[frontend] → 顯示行程卡片
```

`itinerary.py` 不直接呼叫 Claude API，而是透過 `backend/app/llm_provider.py` 的 `LLMProvider`
介面：`AnthropicProvider`（真的呼叫 API，需要 key，會花錢）／`StaticDemoProvider`（不花錢，回傳
`demo_fixtures.py` 裡預先推演好的示範行程）。`get_llm_provider()` 依有沒有 `ANTHROPIC_API_KEY`
自動選擇。之後要加本地免費 LLM（如 Ollama），只要新增一個 Provider 類別即可，不用動其他程式碼。

## 4. 爬蟲合規策略（對應與使用者討論結果）

- **A 級（直接用，零風險）**：OpenStreetMap Overpass API、Wikipedia/Wikivoyage API
- **B 級（謹慎爬，遵守 robots.txt + 限速）**：沖繩觀光局官網、景點/餐廳官網
- **C 級（不碰）**：Google Maps 網頁、Tripadvisor、食べログ、Booking.com/Agoda — 這些 ToS 明文禁止爬蟲且有實際告發紀錄；飯店資料改以 Excel 種子資料＋官網基本資訊為主，數量精簡（20–30間）不追求大量覆蓋

## 5. LLM 成本護欄

1. Anthropic Console 設定 Spend Limit（硬上限）
2. `enrich_llm.py` 為一次性批次任務，結果快取進 JSON，不重複呼叫
3. `itinerary.py` 呼叫前，`filters.py` 必須先把候選景點縮小到 10–15 筆以內才組 prompt
4. 開發階段一律用 Haiku，只有最終生成品質不足時才評估升級 Sonnet

## 6. 工程原則（MVP 階段優先順序）

依使用者要求，本階段程式碼以下列原則檢驗，優先於「功能多寡」：

1. **專案目錄結構**：`docs/`（文件）／`data/`（知識庫本體）／`scraper/`（擷取與標註，離線批次工具）／`backend/`（API 服務）／`frontend/`（網頁），各自獨立資料夾，不混雜
2. **可擴充性**：新功能盡量用「加一個新檔案/新類別」達成，而不是改動既有邏輯。例：`LLMProvider` 之後加 Ollama 只需新增類別；`scraper/sources/` 之後加新來源只需新增檔案
3. **程式可讀性**：每個檔案開頭用一段簡短說明「這是幹嘛的、為什麼這樣設計」（尤其是非顯而易見的決策，如成本護欄、地理合理性檢查），不寫廢話註解
4. **每個功能獨立**：過濾邏輯（`filters.py`）、生成邏輯（`itinerary.py`）、模型呼叫（`llm_provider.py`）、資料模型（`models.py`）分開檔案，各自可獨立測試
5. **後續方便新增新功能**：資料 schema（`data/schema.md`）、API 合約（Pydantic models）都寫清楚，新增功能時看文件就知道現有欄位/介面，不用重新讀懂全部程式碼
6. **單檔案不超過 600 行**：目前最大檔案是 `demo_fixtures.py`（170 行），其餘都在 150 行以內，仍有充裕空間

## 7. 環境需求

- Node.js（已裝 v24）
- Python 3.12（已透過 winget 安裝完成）
- Anthropic API Key（需使用者自行提供，並設定 spend limit）
