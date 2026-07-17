# Changelog

格式依循 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.1.0/)，版本號依循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

## 維護方式

- **每個有意義的 commit/PR 都要留一筆**，不是每天寫一次
- 條目歸類到 `Added`／`Changed`／`Fixed`／`Removed` 之一，用一句話講清楚「做了什麼、為什麼」
- 還沒正式 tag 版本號的變更放在 `[Unreleased]`；每次 tag 新版本時，把 `[Unreleased]` 內容移到對應版本號區塊
- 這裡記的是「對使用者/開發者有感的變化」，不是逐行程式碼異動（那是 git log 的事）

## [Unreleased]

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
