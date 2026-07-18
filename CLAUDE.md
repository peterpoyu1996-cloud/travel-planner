# CLAUDE.md

給 Claude Code（及任何協作者/未來的自己）在這個 repo 裡工作時遵守的規則。跟 [ARCHITECTURE.md](docs/ARCHITECTURE.md) 的關係：那份講「為什麼這樣設計」，這份講「動手寫的時候要照什麼規矩」。

## 專案是什麼

沖繩試點的旅遊決策助手 MVP，見 [docs/PRD.md](docs/PRD.md)。個人專案/作品集性質，零基礎設施成本原則。改動範圍/新增大功能前，先確認有沒有違反 PRD 的 Out of Scope（PRD 第4節）。

## 資料夾結構（新增檔案要放對地方）

```
docs/        需求與架構文件，不放程式碼
data/        知識庫 JSON 本體 + schema.md，不放程式碼
common/      backend 跟 scraper 都要用的共用 Python 套件（目前是 common/geo/，距離/路線計算）
scraper/     離線批次工具（爬蟲、資料標註），不對外提供 API
backend/     FastAPI 服務，對外的唯一入口
frontend/    React + Vite + TypeScript
.github/     CI、PR/Issue 範本
```

新增功能時：能不能用「加一個新檔案」解決，而不是改動既有檔案？（見 ARCHITECTURE.md 第6節可擴充性原則）

## Coding Style

### Python（`backend/`、`scraper/`）
- 需要 type hints，用 `list[dict]`、`str | None` 這種現代語法（Python 3.12+），不用 `Optional[...]`/`List[...]`
- 檔案開頭可以有一段簡短說明「這是幹嘛的、為什麼這樣設計」，只寫非顯而易見的決策（成本護欄、合規考量等），不寫廢話
- 函式/變數 `snake_case`，類別 `PascalCase`
- 路徑操作用 `pathlib.Path`，不用 `os.path`
- 印出訊息用 `print(f"[模組名] ...")` 格式方便追蹤來源（現有程式碼都這樣做）

### TypeScript / React（`frontend/`）
- Function components + hooks，不寫 class component
- 元件檔案 `PascalCase.tsx`，工具/型別檔案 `camelCase.ts`
- 簡單資料形狀用 `type`，不用 `interface`（除非要 extends）
- 元件放 `src/components/`，型別放 `src/types.ts`，API 呼叫集中在 `src/api.ts`，不要在元件裡直接寫 `fetch`

## 資料完整性（硬性規則，不可違反）

- **不可以用猜測值填資料欄位**（座標、評分、地址等）。不確定就填 `null`，在 `source_note` 標來源
- 新資料要標明 `source` 欄位（`excel_seed` / `osm` / `official_site` / `llm_enriched`）
- 爬蟲/比對邏輯如果可能誤配（例如連鎖店多分店），要做合理性檢查（見 `scraper/merge_osm.py` 的地理區域檢查範例），寧可留空不留錯

## 爬蟲合規分級（見 ARCHITECTURE.md 第4節）

- 🟢 A級（OSM/Wikipedia 等開放資料）可直接用
- 🟡 B級（一般官網）要先查 `robots.txt`、限速、誠實標示 User-Agent
- 🔴 C級（Google Maps、Tripadvisor、食べログ、Booking.com/Agoda 等 ToS 明文禁止爬蟲的網站）**絕對不碰**

## LLM 成本護欄（見 ARCHITECTURE.md 第5節）

- 改動 `backend/app/itinerary.py` 或 `scraper/enrich_llm.py` 前，確認呼叫 LLM 之前候選/輸入已經被縮小到合理範圍（現行是 filters.py 限制在 <=15 筆）
- 新增任何會呼叫付費 API 的批次腳本，都要有 `--limit` 這種硬性上限參數
- 預設用 Haiku，不要沒理由就換成更貴的模型

## 架構原則（詳見 ARCHITECTURE.md 第6節，這裡是精簡版）

1. 目錄結構各自獨立，不混雜
2. 新功能優先用「加檔案/加類別」而非改動既有邏輯（例：`LLMProvider` 之後加 Ollama 只需新增類別）
3. 檔案開頭簡短說明「為什麼」，不寫廢話註解
4. 過濾/生成/模型呼叫/資料模型分開檔案，各自獨立
5. **單一檔案不超過 600 行**，接近上限要考慮拆分

## Commit 規則

用 [Conventional Commits](https://www.conventionalcommits.org/zh-hant/)，格式：

```
<type>(<scope>): <簡短描述，祈使句，不要句號>
```

**type**（不可以寫 `update`、`fix stuff` 這種不具體的訊息）：

| type | 用途 |
|---|---|
| `feat` | 新功能 |
| `fix` | 修 bug |
| `refactor` | 不改變行為的程式碼重構 |
| `docs` | 只改文件 |
| `test` | 新增/修改測試 |
| `chore` | 雜項（依賴更新、設定檔調整等） |
| `style` | 純格式調整（不影響邏輯） |
| `perf` | 效能優化 |
| `build` / `ci` | 建置流程、CI 設定 |

**scope** 用受影響的資料夾：`backend`、`frontend`、`scraper`、`data`、`docs`。

範例：
```
feat(backend): add swappable LLM provider with free demo fallback
fix(scraper): reject cross-region false matches in OSM name matching
docs(architecture): record LLM provider abstraction decision
chore: add MIT license
```

## 文件維護責任

| 文件 | 何時更新 |
|---|---|
| `docs/PRD.md` | 範圍/需求改變時，需使用者確認再改（這是決策文件，不是自己想改就改） |
| `docs/ARCHITECTURE.md` | 新增架構層級的決策時（不是每次改程式碼） |
| `docs/ROADMAP.md` | 完成一個里程碑時 |
| `CHANGELOG.md` | 每個有意義的 commit/PR |
| `CLAUDE.md` | 專案規則本身改變時（例如新增新的語言/框架） |
