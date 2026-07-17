# 旅遊決策助手（沖繩試點）

輸入旅遊條件（日期、住宿地、是否租車、是否帶小孩、預算、目前所在地），從沖繩景點/飯店/餐廳知識庫中生成多日行程建議。MVP 階段聚焦「根據條件生成靠譜行程」，即時天氣/營業時間動態改建議列入後續階段（見 [ROADMAP.md](docs/ROADMAP.md)）。

個人專案／作品集性質，技術決策以零基礎設施成本、LLM 呼叫成本可忽略為原則（見 [ARCHITECTURE.md](docs/ARCHITECTURE.md)）。

## 文件導覽

| 文件 | 用途 |
|---|---|
| [docs/PRD.md](docs/PRD.md) | 需求文件：問題定義、範圍、功能需求、資料需求 |
| [docs/USER_FLOW.md](docs/USER_FLOW.md) | 使用流程與邊界情境 |
| [docs/MVP.md](docs/MVP.md) | 這個版本該做/不該做什麼（優先級清單） |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 技術架構決策、資料流、工程原則 |
| [docs/ROADMAP.md](docs/ROADMAP.md) | 現在做到哪、接下來做什麼（時間軸導向） |
| [CHANGELOG.md](CHANGELOG.md) | 每個有意義變更的記錄 |
| [CLAUDE.md](CLAUDE.md) | 專案規則：coding style、資料夾/命名慣例、commit 規則 |

## 專案結構

```
travel-planner/
├── docs/            需求與架構文件
├── data/            知識庫本體（JSON，人工可讀可編輯）＋ schema 定義
├── scraper/         Python 爬蟲與資料標註批次工具
├── backend/         FastAPI 服務
├── frontend/        React + Vite + TypeScript 網頁
└── .github/         CI workflow、PR/Issue 範本
```

## 快速開始

### 後端

```bash
python -m venv .venv
./.venv/Scripts/pip install -r backend/requirements.txt -r scraper/requirements.txt
./.venv/Scripts/python -m uvicorn backend.app.main:app --reload --port 8000
```

沒有設定 `ANTHROPIC_API_KEY` 時，`/itinerary` 會自動使用不花錢的 Demo Provider 回傳示範行程；設定了才會真的呼叫 Claude API（記得先在 [Anthropic Console](https://console.anthropic.com/) 設定 Spend Limit，見 [ARCHITECTURE.md](docs/ARCHITECTURE.md) 第5節）。

```bash
export ANTHROPIC_API_KEY=sk-ant-...   # PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

預設會打 `http://localhost:8000`，可用 `.env` 設定 `VITE_API_BASE` 覆蓋。

### 爬蟲／資料工具

```bash
./.venv/Scripts/python scraper/sources/osm_overpass.py     # 抓 OSM 開放資料
./.venv/Scripts/python scraper/merge_osm.py                 # 合併座標進知識庫
./.venv/Scripts/python scraper/enrich_llm.py --file data/attractions.json --limit 10  # 需 API key
```

## License

[MIT](LICENSE)
