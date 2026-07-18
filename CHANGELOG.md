# Changelog

格式依循 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.1.0/)，版本號依循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

## 維護方式

- **每個有意義的 commit/PR 都要留一筆**，不是每天寫一次
- 條目歸類到 `Added`／`Changed`／`Fixed`／`Removed` 之一，用一句話講清楚「做了什麼、為什麼」
- 還沒正式 tag 版本號的變更放在 `[Unreleased]`；每次 tag 新版本時，把 `[Unreleased]` 內容移到對應版本號區塊
- 這裡記的是「對使用者/開發者有感的變化」，不是逐行程式碼異動（那是 git log 的事）

## [Unreleased]

### Added
- 把知識庫 `name` 欄位轉成繁體中文：`scraper/convert_traditional.py`（機械式新字體→繁體字元替換）+ `scraper/translate_names.py`（LLM輔助翻譯，僅翻有把握的知名連鎖店/地標）
- 用 WebSearch/WebFetch 研究官方網站/部落格，補齊 6 筆熱門景點的 MapCode/停車/營業時間等核心欄位（首里城公園、齋場御嶽、沖繩世界玉泉洞、姬百合和平祈念資料館、殘波岬、真榮田岬）
- 新增 `translated_name` 欄位，保證 UI 顯示一定是中文，跟謹慎保守的 `name` 欄位分開（`scraper/add_translated_name.py`）
- 針對「不開車行程」缺口新增地基：`scraper/geo_utils.py`（haversine 距離）、`data/transit_stations.json`（單軌電車19站）、`scraper/tag_transit_access.py`（標註每筆資料離最近單軌站多遠），並更新 `filters.py` 讓單軌步行範圍內的景點在 `has_car=false` 時不會被誤排除
- 針對「玩水行程」缺口，OSM 查詢補上 `natural=beach`，新增 25 筆命名海灘到知識庫
- 新增高速公路感知的車程估算：`scraper/build_highway_network.py`（整理路段+交流道）、`scraper/highway_routing.py`（圖論最短路徑算交流道間實際公路距離）、`scraper/travel_time.py`（比較平面道路 vs 上下高速兩種路線取較快者，高速90km/h／平面45km/h）
- 新增 `scraper/draw_map.py`：把高速公路、交流道、183筆有座標的知識庫資料畫成地圖，存於 `docs/assets/okinawa_knowledge_map.png`

### Fixed
- 修正 2 筆 OSM 社群提供的 `name:zh` 標籤形近字誤植（案本食堂→岸本食堂、花苙→花笠食堂）
- `ingest_osm.py` 的 `to_entry()` 補上對 way/relation（`out center` 查詢回傳座標在 `center` 而非頂層）的座標解析，海灘資料需要這個
- 補上「美麗海水族館」「泊港漁市場」長期缺失的經緯度（查證自官網），這兩筆之前因為 merge_osm.py 的地理區域檢查正確擋掉了錯誤配對，但一直沒有補上正確座標
- `travel_time.py` 原本只試離起訖點最近的1個交流道，遇到 OSM 資料裡沒連通的交流道就會整個判斷失敗、誤回報「沒有更快的高速公路路線」，改成試最近的5個組合

## [0.2.0] - 2026-07-18

### Added
- 建立 GitHub repo 治理文件：README、CLAUDE.md（專案規則）、ROADMAP、Conventional Commits 規範、CI（backend/frontend build check）、PR/Issue 範本
- 前端新增 4 個預先產生的範例情境按鈕（夫妻開車/不開車、四口之家玩水、六口之家老少平衡），零 API 成本、即點即看
- 重新設計行程顯示與表單 UI（分頁、卡片、深色模式）
- 新增 `scraper/ingest_osm.py`：從 OSM 原始資料匯入廣度資料，知識庫從 15 筆擴充到 165 筆（景點67/飯店33/餐廳65）
- `region_group` 標準化為沖繩本島標準三分法（北部/中部/南部），細節搬到新的 `sub_area` 欄位

### Fixed
- `filters.py`：`has_car=false` 時原本誤用「有沒有停車場」判斷能不能去，跟真正的「需不需要開車」邏輯無關，已修正為直接依 `travel_mode` 排除
- `scraper/ingest_osm.py` 去重比對從精確字串相等改成雙向子字串包含，修正「大家」誤配到已存在種子資料「百年古家 大家」的重複問題

### Changed
- 個人行程 Excel 原始檔從 git 歷史完整移除（改用 `git filter-branch`），避免公開 repo 外流個人資料，只保留去識別化後的 JSON

## [0.1.0] - 2026-07-18

### Added
- 建立 PRD、User Flow、MVP 範圍文件（沖繩試點）
- 建立零成本技術架構決策文件（Node/Python 全端、規則式過濾取代向量 RAG、爬蟲合規分級）
- 建立知識庫 schema，並將使用者真實沖繩行程 Excel 轉為結構化種子資料（7 景點/5 餐廳/3 飯店）
- 建立 OSM Overpass 爬蟲，補齊景點座標，並加入地理區域合理性檢查避免連鎖店誤配
- 建立 B 級官網爬蟲骨架與 robots.txt 合規檢查工具
- 建立 FastAPI 後端：規則式候選過濾（`filters.py`）、行程生成（`itinerary.py`）
- 建立可抽換 LLM Provider 架構（`llm_provider.py`），支援真實 Claude API 與免費 Demo 模式，成本護欄透過候選數量限制與 Spend Limit 建議控制
- 建立 React + Vite + TypeScript 前端：行程條件表單、行程卡片顯示、API client
- 完成前後端端對端驗證（health check、CORS、Demo Provider 完整生成流程）
