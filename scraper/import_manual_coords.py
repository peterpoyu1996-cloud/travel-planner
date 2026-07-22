"""讀 data/private/manual_poi_coords.yaml（使用說明見該檔案開頭），把使用者手動
提供的地址/座標補進知識庫。跟 fill_missing_coords.py（全自動打 OSM/Nominatim）
互補：這支是給「自動查不到，需要人補線索」的剩餘案例用的最後一道手動流程。

安全機制：
1. source_hint 必填，且不能出現「google」字樣——這個檔案存在的目的就是繞開
   Google Maps 這個唯一有資料但被 CLAUDE.md 列為禁用來源的地方，這個檢查是
   防呆，避免日後忘記規則、把 Google 來源的資料混進來。
2. 有給地址的話，一樣套用 merge_osm.py 的 region_group 地理合理性檢查，避免
   使用者提供的地址剛好對應到別的地方（例如連鎖店打錯分店地址）。
3. 只補「現在確實是 null」的欄位，不覆寫任何已有座標的紀錄。
4. 成功匯入的條目會從 yaml 檔案移除（用文字區塊比對，保留其他條目跟開頭的
   使用說明註解不被 yaml.dump 洗掉——PyYAML 序列化不保留註解，所以不能整檔
   load 完再 dump 回去）。
"""

import json
import re
import sys
import time
from pathlib import Path

import requests
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from merge_osm import in_region  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
INPUT_PATH = DATA_DIR / "private" / "manual_poi_coords.yaml"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "travel-planner-okinawa-mvp/0.1 (personal portfolio project)"
NOMINATIM_DELAY_SEC = 1.1

CATEGORY_FILES = {
    "attraction": "attractions.json",
    "restaurant": "restaurants.json",
    "hotel": "hotels.json",
}


def load_kb() -> dict[str, tuple[dict, str]]:
    """回傳 {id: (entry_dict, category)}，entry_dict 是同一個物件參照，
    改它就是改記憶體裡準備寫回檔案的那份資料。
    """
    index: dict[str, tuple[dict, str]] = {}
    for category, filename in CATEGORY_FILES.items():
        entries = json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))
        for entry in entries:
            index[entry["id"]] = (entry, category)
    return index


def geocode_address(address: str) -> tuple[float, float] | None:
    resp = requests.get(
        NOMINATIM_URL,
        params={"q": address, "format": "json", "limit": 3, "countrycodes": "jp"},
        headers={"User-Agent": USER_AGENT},
        timeout=20,
    )
    resp.raise_for_status()
    time.sleep(NOMINATIM_DELAY_SEC)
    results = resp.json()
    return results


def split_entry_blocks(raw_text: str) -> tuple[str, list[tuple[str, str]]]:
    """把原始 yaml 文字切成 (header, [(entry_id, entry_text_block), ...])。
    entry 的判定：每一筆頂層清單項目都是行首（沒有縮排）的 "- id: xxx"。
    用文字區塊而不是 yaml.dump 重組，是為了不破壞使用者手動加的註解跟開頭說明。
    """
    lines = raw_text.splitlines(keepends=True)
    start_pattern = re.compile(r"^- id:\s*(\S+)")

    entry_starts = [i for i, line in enumerate(lines) if start_pattern.match(line)]
    if not entry_starts:
        return raw_text, []

    header = "".join(lines[: entry_starts[0]])
    blocks = []
    for idx, start in enumerate(entry_starts):
        end = entry_starts[idx + 1] if idx + 1 < len(entry_starts) else len(lines)
        entry_id = start_pattern.match(lines[start]).group(1)
        blocks.append((entry_id, "".join(lines[start:end])))

    return header, blocks


def main() -> None:
    if not INPUT_PATH.exists():
        print(f"[import_manual_coords] 找不到 {INPUT_PATH}，沒有東西可匯入")
        return

    raw_text = INPUT_PATH.read_text(encoding="utf-8")
    header, blocks = split_entry_blocks(raw_text)
    parsed_entries = yaml.safe_load(raw_text) or []

    if len(parsed_entries) != len(blocks):
        print("[import_manual_coords] 內部錯誤：解析出的條目數跟文字區塊數對不上，為安全起見中止，不寫入任何檔案")
        return

    kb_index = load_kb()
    changed_categories: set[str] = set()
    kept_blocks: list[str] = []

    for parsed, (block_id, block_text) in zip(parsed_entries, blocks):
        entry_id = parsed.get("id")
        if entry_id == "_example":
            kept_blocks.append(block_text)  # 範例區塊永遠保留，不處理
            continue

        print(f"[import_manual_coords] 處理 {entry_id}")

        if entry_id not in kb_index:
            print(f"[import_manual_coords]   找不到這個 id，知識庫裡沒有 {entry_id!r}，跳過（保留在檔案裡，檢查是不是打錯字）")
            kept_blocks.append(block_text)
            continue

        source_hint = (parsed.get("source_hint") or "").strip()
        if not source_hint:
            print("[import_manual_coords]   source_hint 沒填，跳過（這欄必填，才知道資料哪裡來的）")
            kept_blocks.append(block_text)
            continue
        if "google" in source_hint.lower():
            print("[import_manual_coords]   source_hint 提到 google，這個檔案不接受 Google 來源的資料，跳過")
            kept_blocks.append(block_text)
            continue

        entry, category = kb_index[entry_id]
        if entry.get("lat") is not None and entry.get("lng") is not None:
            print("[import_manual_coords]   知識庫裡這筆已經有座標了，不覆寫，跳過")
            kept_blocks.append(block_text)
            continue

        address = (parsed.get("address") or "").strip()
        has_coords = parsed.get("lat") is not None and parsed.get("lng") is not None

        if bool(address) == has_coords:
            print("[import_manual_coords]   address 跟 lat/lng 要二選一（不能兩個都填或都空），跳過")
            kept_blocks.append(block_text)
            continue

        region_group = entry.get("region_group", "")

        if has_coords:
            lat, lng = float(parsed["lat"]), float(parsed["lng"])
            if not in_region(lat, region_group):
                print(f"[import_manual_coords]   你提供的座標 ({lat}, {lng}) 不在「{region_group}」的合理緯度範圍內，可能填錯了，跳過不寫入")
                kept_blocks.append(block_text)
                continue
            method = f"使用者提供座標（{source_hint}）"
        else:
            try:
                results = geocode_address(address)
            except requests.RequestException as e:
                print(f"[import_manual_coords]   查地址失敗：{e}，跳過")
                kept_blocks.append(block_text)
                continue

            match = next((r for r in results if in_region(float(r["lat"]), region_group)), None)
            if not match:
                if results:
                    print(f"[import_manual_coords]   地址查到 {len(results)} 個結果，但都不在「{region_group}」合理緯度範圍內，可能地址不夠精確，跳過")
                else:
                    print("[import_manual_coords]   地址查無結果，跳過（可以試試更完整的地址，或改填 lat/lng）")
                kept_blocks.append(block_text)
                continue
            lat, lng = float(match["lat"]), float(match["lon"])
            method = f"Nominatim 地址查詢（{source_hint}）"

        entry["lat"] = lat
        entry["lng"] = lng
        base_note = (entry.get("source_note") or "").rstrip("；")
        note = f"lat/lng 由{method}補齊"
        entry["source_note"] = f"{base_note}；{note}" if base_note else note
        changed_categories.add(category)
        print(f"[import_manual_coords]   -> 補上 ({lat}, {lng})，已從待處理清單移除")
        # 成功的不加進 kept_blocks，等於從檔案裡刪掉

    for category in changed_categories:
        path = DATA_DIR / CATEGORY_FILES[category]
        entries = [e for e, c in kb_index.values() if c == category]
        path.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[import_manual_coords] 已寫回 {path}")

    INPUT_PATH.write_text(header + "".join(kept_blocks), encoding="utf-8")
    print(f"[import_manual_coords] 完成，{INPUT_PATH} 已更新（成功匯入的條目已移除）")


if __name__ == "__main__":
    main()
