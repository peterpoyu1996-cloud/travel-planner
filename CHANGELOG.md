# Changelog

格式依循 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.1.0/)，版本號依循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

## 維護方式

- **每個有意義的 commit/PR 都要留一筆**，不是每天寫一次
- 條目歸類到 `Added`／`Changed`／`Fixed`／`Removed` 之一，用一句話講清楚「做了什麼、為什麼」
- 還沒正式 tag 版本號的變更放在 `[Unreleased]`；每次 tag 新版本時，把 `[Unreleased]` 內容移到對應版本號區塊
- 這裡記的是「對使用者/開發者有感的變化」，不是逐行程式碼異動（那是 git log 的事）

## [Unreleased]

### Removed
- 修正先前對`トリップショットヴィラズ・ハマヒガ`的誤判：前一輪營業真實性查核時因OTA平台仍顯示可訂而判斷為過時謠言未刪除，但補`recommendation_score`時同一則2024/6/6停業消息帶著更具體細節再度獨立浮現，判斷可信度足夠後翻案改為確認停業並刪除（飯店筆數32→31）。教訓：孤立的「查無反證」不能當作「這件事沒發生」的證明
- 刪除已確認停業的飯店條目 `うたごえペンションまーみなー`（osm-hotel-12008683880）：查證確認已於2025年11月結束營業，原址改為不同業態的「歌声の店」，飯店筆數33→32。這是針對33筆飯店/民宿類做一次完整「營業真實性」查核的結果——另確認2筆先前被誤標「可能歇業」的景點（清ら海ファーム/諸見民藝館）其實仍在營業已修正備註、1筆品牌更名非歇業（沖縄読谷デザイナーズコンドミニアムホテル→CHULAX沖縄読谷）；查證方法與逐筆結論見 `data/schema.md`「營業真實性查核與停業條目清理」一節

### Added
- 第四批（使用者要求「全部逐筆查證」）：完成知識庫剩餘全部176筆`recommendation_score`查證（景點83/飯店28/餐廳65），用中性關鍵字（評価/口コミ/がっかり/微妙）查證並重用Tabelog/じゃらん/TripAdvisor/NAVITIME等平台既有評分數字佐證；25筆海灘沿用P0-P2階段既有安全設施查證資料換算分數（無人管理但風景知名的秘境海灘給予中等分數反映「風景好但需自負風險」的真實落差）。累計完成度164/204（80%），剩餘40筆記錄查證嘗試理由於source_note；過程中發現2筆餐廳（`cafe帆風`、`YOMITAN魔女カレー恵庵`）有營業狀態存疑訊號，刻意不給推薦度分數並標記待未來追蹤
- 新增 `recommendation_score` 欄位（0-5，0.1級距，null預設）：跟 `kid_friendly` 星等制同方法論（WebSearch/WebFetch交叉查證≥3篇獨立來源），但衡量「一般推薦度」而非「帶小孩好不好」，刻意用不含「親子」的中性/負面關鍵字（評価/口コミ/がっかり/微妙/つまらない）查證避免結論被親子情境污染；跟結構性缺口的 `rating` 欄位不同（`rating`需要C級來源才有的評分數字，合規來源查不到；`recommendation_score`是自己交叉比對出的質化分數）；累計完成29筆試點，方法論見 `data/schema.md`「recommendation_score（一般推薦度）」一節。齋場御嶽（kid_friendly 1.8 / recommendation_score 4.4）與舊海軍司令部壕（kid_friendly 未設值 / recommendation_score 4.5）是兩欄位分歧最明顯的案例——世界遺產聖地與戰爭史蹟對小小孩不見得合適，但對一般成人遊客評價極高，證明這兩條軸線缺一不可
- 第五批（使用者要求「全部逐筆查證」）：完成知識庫剩餘**全部**景點/飯店/餐廳的kid_friendly首次查證掃描，累計95/206（46%）。過程中意外發現兩筆重要資料時效性問題：`グランディスタイル沖縄読谷ホテル`2024/4起改為僅限13歲以上入住（星等改為1.0反映現行政策）、`うたごえペンションまーみなー`已於2025/11停業（不填值，建議標記歇業）；另確認`アスムイハイクス`與`daisekirinzan`座標/營業時間完全相同為重複OSM節點，建議合併。剩餘111筆全部記錄查證嘗試與查無資料的具體理由於source_note，不是遺漏
- 第四批 kid_friendly 星等查證累計完成54筆：15筆海灘直接沿用P0-P2階段已查證的安全設施資料換算星等（不重新搜尋），另新增12筆知名景點（心形岩/殘波岬/真榮田岬/海中道路/金城町石畳道/沖繩便便博物館/Little Universe/森林アドベンチャー/ジャングリア恐竜サファリ/泊いゆまち/オリオンハッピーパーク），不屈館比照戰爭史蹟原則不設數值；誠實記錄17筆因地址缺失/名稱過於通用/查無獨立敘事而留null的案例，反映原始OSM資料本身的結構性限制
- 第三批 kid_friendly 星等查證累計完成28筆（新增14筆：美麗海村公寓/瀨長島飯店/古宇利塔/齋場御嶽/東南植物樂園/沖繩世界玉泉洞/OKINAWAフルーツらんど/ナゴパイナップルパーク/体験王國むら咲むら/ビオスの丘/4個認證海灘），戰爭史蹟舊海軍司令部壕沿用既有原則不設數值改寫kid_age_notes，另1筆(那覇日航シティホテル)因證據不足留null
- `kid_friendly` 從 `true/false/null` 改成 0-5 星等（先0.5級距，使用者回饋「太粗」後改為0.1級距）+ null，舊布林值保留於新增的 `kid_friendly_legacy_flag`（不機械轉換，避免變相猜測）；用 WebSearch/WebFetch 交叉查證至少3篇獨立部落格網域，累計完成14筆試點（含使用者指名的DINO恐竜PARK恐龍公園、美麗海水族館、琉球村、國際通、首里城公園、沖繩兒童王國、AEON MALL來客夢、蒙特雷飯店、Hilton瀬底等），另有5筆（2間商務飯店、3間燒肉店）因缺乏獨立敘事型部落格佐證誠實留null；評分邏輯與爬蟲來源合規分級見 `data/schema.md`「kid_friendly 星等制」一節；同步修正 `backend/app/filters.py` 的 `matches_conditions()`，過渡期同時檢查新星等與舊布林值，避免星等制上線後海灘安全性等既有排除邏輯失效
- 匯入沖縄県観光施設一覧開放資料（CC-BY 4.0）：升級6筆既有景點（首里城公園/美麗海水族館/舊海軍司令部壕/東南植物樂園/沖繩世界玉泉洞/古宇利塔）的停車場/票價/營業時間/無障礙資訊，新增10筆全新景點（含使用者指名缺少的DINO恐竜PARKやんばる亜熱帯の森恐龍公園），新增 `accessibility_notes` 欄位；`budget_level` 直接用官方票價換算，不是猜的
- 匯入沖縄縣警察廳「安全對策優良海域レジャー提供業者(マル優業者)一覧表」（官方持續更新）：新增4筆最高安全等級認證海灘（ブセナビーチ/恩納海浜公園ナビービーチ/オクマビーチ/万座ビーチ），交叉驗證既有かりゆしビーチ的安全資料
- 補上使用者指名的知識庫缺口 KOURI SHRIMP（古宇利島蝦蝦飯），查證自官網 lovesokinawa.co.jp，並校正多個二手網站誤植的行政區（本部町→今帰仁村）
- 把知識庫 `name` 欄位轉成繁體中文：`scraper/convert_traditional.py`（機械式新字體→繁體字元替換）+ `scraper/translate_names.py`（LLM輔助翻譯，僅翻有把握的知名連鎖店/地標）
- 用 WebSearch/WebFetch 研究官方網站/部落格，補齊 6 筆熱門景點的 MapCode/停車/營業時間等核心欄位（首里城公園、齋場御嶽、沖繩世界玉泉洞、姬百合和平祈念資料館、殘波岬、真榮田岬）
- 新增 `translated_name` 欄位，保證 UI 顯示一定是中文，跟謹慎保守的 `name` 欄位分開（`scraper/add_translated_name.py`）
- 針對「不開車行程」缺口新增地基：`scraper/geo_utils.py`（haversine 距離）、`data/transit_stations.json`（單軌電車19站）、`scraper/tag_transit_access.py`（標註每筆資料離最近單軌站多遠），並更新 `filters.py` 讓單軌步行範圍內的景點在 `has_car=false` 時不會被誤排除
- 針對「玩水行程」缺口，OSM 查詢補上 `natural=beach`，新增 25 筆命名海灘到知識庫
- 新增高速公路感知的車程估算：`scraper/build_highway_network.py`（整理路段+交流道）、`scraper/highway_routing.py`（圖論最短路徑算交流道間實際公路距離）、`scraper/travel_time.py`（比較平面道路 vs 上下高速兩種路線取較快者，高速90km/h／平面45km/h）
- 新增 `scraper/draw_map.py`：把高速公路、交流道、183筆有座標的知識庫資料畫成地圖，存於 `docs/assets/okinawa_knowledge_map.png`
- 把 `geo_utils.py`／`highway_routing.py`／`travel_time.py` 從 `scraper/` 搬到新的 `common/geo/` 套件（backend 跟 scraper 都要用，不該只放在 scraper 底下），並把 `travel_time.py` 接進 `backend/app/itinerary.py`：行程生成後，用真實座標＋高速公路網路重新算每天相鄰站點的車程，覆蓋掉 LLM 填的版本，已用真實 HTTP API 請求驗證過
- 新增 `AEON MALL沖繩來客夢`（`aeon-mall-okinawa-rycom`）到 `data/attractions.json`：地址/MapCode 查證自官網 `okinawarycom.aeonmall.jp`，座標交叉核對 NAVITIME（官網未提供十進位經緯度）
- 前端／後端示範情境（`frontend/src/data/demoScenarios.ts`、`backend/app/demo_fixtures.py`）整套換成新範例：兩大一小(6歲)自駕南玩到北再回來、五天四夜，含國際通/海灘飯店/美麗海水族館/購物中心/動物園/燒肉，站間車程用 `common/geo/travel_time.py` 實際算過，取代原本 4 個舊情境按鈕
- 前端新增第二個對照範例 `chat-raw-comparison`：同一個 prompt 直接丟給 Claude Chat（未使用知識庫、未查證）得到的原始回答逐字轉錄，跟系統產出的範例並排比較用，stop id 一律用 `chat-` 前綴跟真實知識庫 id 區隔
- 新增 `start-dev.bat`（連同 `backend/run-backend.bat`、`frontend/run-frontend.bat`）：雙擊即可同時啟動後端/前端並自動開瀏覽器，純開發便利腳本
- 新增 `.github/workflows/deploy-pages.yml`：push 到 main 時自動把前端建置後部署到 GitHub Pages（純靜態、免費）。只有前端，後端沒有一起部署，公開網址上「自訂條件生成」表單會因為呼叫不到 API 而顯示錯誤訊息，「範例情境」（不呼叫 API）功能完全正常；`vite.config.ts` 加上 `base: '/travel-planner/'`（僅限 build，dev server 不受影響）
- `backend/app/opening_hours_check.py`：行程生成後額外檢查每站 `opening_hours` 有沒有整天公休，跟該天實際星期幾比對，兜不上就加進 warnings；只做得到「星期幾層級」的檢查，抓不到「同一天不同時段」的衝突（例如平日只有晚餐、假日才有午餐這種），因為 Stop 目前沒有結構化的到站時間欄位，是已知限制
- 大規模補齊決策相關欄位（見 `data/schema.md`「決策相關欄位補標」一節）：`kid_friendly` 從 3/191 補到 98/191（AI 依景點類型判斷，戰爭主題資料館用 `kid_age_notes` 而非直接判false）；25筆海灘先全部標記可能親子友善，再用 WebSearch 查證 16 筆的實際監視員/防水母網/淋浴廁所安全設施，其中 11 筆查到「沒有監視員」等風險訊號後改回 null/false 並寫入新用到的 `conditional_note`；`budget_level` 針對有真實價格根據的連鎖餐廳與2筆已知餐廳補到 11/191；`mapcode`/`has_parking` 針對兩個範例情境會用到的候選逐筆查證官網

### Fixed
- 修正 2 筆 OSM 社群提供的 `name:zh` 標籤形近字誤植（案本食堂→岸本食堂、花苙→花笠食堂）
- `ingest_osm.py` 的 `to_entry()` 補上對 way/relation（`out center` 查詢回傳座標在 `center` 而非頂層）的座標解析，海灘資料需要這個
- 補上「美麗海水族館」「泊港漁市場」長期缺失的經緯度（查證自官網），這兩筆之前因為 merge_osm.py 的地理區域檢查正確擋掉了錯誤配對，但一直沒有補上正確座標
- `travel_time.py` 原本只試離起訖點最近的1個交流道，遇到 OSM 資料裡沒連通的交流道就會整個判斷失敗、誤回報「沒有更快的高速公路路線」，改成試最近的5個組合
- `filters.select_candidates()` 原本直接 `[:limit]` 截斷，知識庫擴充到190+筆、`attractions.json` 資料量獨大之後，候選清單會整個被景點佔滿、完全排不進飯店/餐廳，改成跨分類輪流挑選（同時依資料完整度排序，excel_seed/官網查證過的資料優先）
- `itinerary.fill_real_travel_times()` 原本只算「同一天內」相鄰站點的車程，前一晚住宿到隔天第一站（跨 `DayPlan` 邊界）完全沒算、`travel_time_from_prev` 會是 null，改成把整趟行程攤平成一條連續序列再算，涵蓋跨天銜接

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
