"""一次性批次任務：用 LLM 幫忙補主觀判斷欄位
（kid_friendly / indoor_outdoor / budget_level / description_for_embedding）。

成本護欄（對應 docs/ARCHITECTURE.md 第5節）：
1. 只處理「還沒被標註過」的資料（llm_enriched != true），不會重複呼叫
2. 用 Haiku，prompt 精簡（只帶單筆資料的既有欄位，不帶整包知識庫）
3. --limit 參數硬性限制單次執行最多呼叫幾次 API（預設 20），避免程式寫壞無限迴圈燒 token
4. 執行前務必已在 Anthropic Console 設定 Spend Limit

使用方式：
    set ANTHROPIC_API_KEY=你的key   (PowerShell: $env:ANTHROPIC_API_KEY="...")
    python enrich_llm.py --file ../data/attractions.json --limit 10
"""

import argparse
import json
import os
from pathlib import Path

import anthropic

MODEL = "claude-haiku-4-5-20251001"

FIELDS_TO_FILL = ["kid_friendly", "indoor_outdoor", "budget_level", "description_for_embedding"]

PROMPT_TEMPLATE = """你是旅遊資料標註助手。根據以下沖繩景點/餐廳/飯店的已知資訊，判斷缺少的欄位。
只能根據提供的資訊合理推論，不確定的欄位請填 null，不要編造具體數字或事實。

已知資訊：
{known_info}

請只回傳一個 JSON 物件，欄位如下，不要有其他文字：
{{
  "kid_friendly": true/false/null,
  "indoor_outdoor": "室內"/"戶外"/"兩者皆有"/null,
  "budget_level": "$"/"$$"/"$$$"/null,
  "description_for_embedding": "一段30-60字的自然語言描述，融合已知資訊，供向量檢索使用，或 null"
}}
"""


def needs_enrichment(entry: dict) -> bool:
    if entry.get("llm_enriched"):
        return False
    return any(entry.get(f) is None for f in FIELDS_TO_FILL)


def build_known_info(entry: dict) -> str:
    keys = [
        "name", "name_local", "category", "region_group", "opening_hours",
        "travel_time_from_prev", "suggested_stay_duration", "parking_notes",
        "conditional_note", "requires_reservation", "kid_age_notes", "source_note",
    ]
    lines = [f"{k}: {entry[k]}" for k in keys if entry.get(k) not in (None, "")]
    return "\n".join(lines)


def enrich_entry(client: anthropic.Anthropic, entry: dict) -> dict:
    prompt = PROMPT_TEMPLATE.format(known_info=build_known_info(entry))
    resp = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text.strip()
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        print(f"[enrich_llm] 無法解析回應，略過 {entry.get('id')}: {text[:100]}")
        return entry

    for field in FIELDS_TO_FILL:
        if field in result and entry.get(field) is None:
            entry[field] = result[field]
    entry["llm_enriched"] = True
    return entry


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="要處理的 JSON 檔案路徑")
    parser.add_argument("--limit", type=int, default=20, help="單次執行最多呼叫幾次 API")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("請先設定環境變數 ANTHROPIC_API_KEY")

    path = Path(args.file)
    entries = json.loads(path.read_text(encoding="utf-8"))

    client = anthropic.Anthropic(api_key=api_key)
    calls_made = 0

    for entry in entries:
        if calls_made >= args.limit:
            print(f"[enrich_llm] 已達 --limit={args.limit}，停止（避免超額呼叫）")
            break
        if not needs_enrichment(entry):
            continue

        print(f"[enrich_llm] 標註中: {entry.get('id')}")
        enrich_entry(client, entry)
        calls_made += 1

    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[enrich_llm] 完成，共呼叫 API {calls_made} 次，寫回 {path}")


if __name__ == "__main__":
    main()
