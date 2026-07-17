"""把知識庫裡還是日文漢字（新字體）的 name 欄位轉成繁體中文。

只處理「純漢字、沒有假名」的名稱，這種轉換是機械式的字元替換（新字體→繁體），
不是翻譯，風險低、可驗證。含假名（片假名/平假名）的名稱通常是音譯外來語或
需要語意翻譯的店名，不在這支腳本處理範圍內，留給人工/LLM 另外處理，
並在 source_note 誠實標註「機械轉換」vs「人工翻譯」的差別。

⚠️ 不要用 OpenCC 的 s2t（簡體→繁體）打底：試過之後發現它會把「首里城」
（沖繩最重要的世界遺產景點）誤轉成「首裏城」——因為簡體中文的「里」同時是
「里」跟「裡/裏」兩個繁體字的簡化結果，OpenCC 沒辦法判斷這裡該用哪個，
直接轉出錯誤結果。这種一對多的簡轉繁天生就會有歧義風險，不適合用在
「新字體→繁體」這種每個字元語意明確、應該要精準對應的場景。

改成只用下面這份「日文新字體 -> 繁體」人工對照表逐字替換，沒有在表裡的字元
一律保留原樣（寧可少轉，也不要轉錯）。
"""

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
KANA_RE = re.compile(r"[぀-ヿ]")  # 平假名+片假名區間

# 日文新字體 -> 繁體中文，OpenCC s2t 沒涵蓋的日本特有簡化字
JP_SHINJITAI_TO_TRADITIONAL = {
    "国": "國", "観": "觀", "縄": "繩", "沢": "澤", "円": "圓", "学": "學", "気": "氣",
    "対": "對", "実": "實", "医": "醫", "済": "濟", "応": "應", "楽": "樂",
    "覇": "霸", "桜": "櫻", "髪": "髮", "蔵": "藏", "竜": "龍", "亀": "龜",
    "温": "溫", "県": "縣", "灯": "燈", "権": "權", "歓": "歡", "伝": "傳",
    "変": "變", "総": "總", "継": "繼", "続": "續", "断": "斷", "単": "單",
    "営": "營", "栄": "榮", "労": "勞", "験": "驗", "険": "險", "剣": "劍",
    "検": "檢", "挙": "舉", "拠": "據", "処": "處", "号": "號", "与": "與",
    "発": "發", "鉄": "鐵", "銭": "錢", "価": "價", "写": "寫", "仏": "佛",
    "払": "拂", "仮": "假", "児": "兒", "隠": "隱", "陥": "陷", "隣": "鄰",
    "声": "聲", "壱": "壹", "参": "參", "収": "收", "従": "從", "徴": "徵",
    "徳": "德", "恋": "戀", "悪": "惡", "戦": "戰", "択": "擇", "拝": "拜",
    "拡": "擴", "撃": "擊", "数": "數", "斉": "齊", "斎": "齋", "旧": "舊",
    "昼": "晝", "曽": "曾", "渋": "澀", "満": "滿", "潜": "潛", "点": "點",
    "焼": "燒", "状": "狀", "独": "獨", "狭": "狹", "献": "獻", "産": "產",
    "画": "畫", "盗": "盜", "砕": "碎", "称": "稱", "税": "稅", "穂": "穗",
    "窃": "竊", "粋": "粹", "糸": "絲", "経": "經", "縁": "緣", "繊": "纖",
    "缶": "罐", "聴": "聽", "胆": "膽", "脳": "腦", "臓": "臟", "舎": "舍",
    "芸": "藝", "荘": "莊", "薬": "藥", "蛍": "螢", "装": "裝", "覚": "覺",
    "触": "觸", "訳": "譯", "証": "證", "読": "讀", "謡": "謠", "譲": "讓",
    "転": "轉", "軽": "輕", "辺": "邊", "遅": "遲", "郷": "鄉", "酔": "醉",
    "醸": "釀", "釈": "釋", "静": "靜", "駅": "驛", "髄": "髓", "鶏": "雞",
    "麦": "麥", "黒": "黑", "黙": "默", "巣": "巢", "帯": "帶", "桟": "棧",
    "桧": "檜", "楼": "樓", "殻": "殼", "毎": "每", "渓": "溪", "畳": "疊",
    "縦": "縱", "蚕": "蠶", "誉": "譽", "賛": "贊", "頬": "頰", "顕": "顯",
    "湾": "灣", "歴": "歷", "残": "殘", "浅": "淺", "区": "區", "関": "關",
    "広": "廣",
}

def convert_text(text: str) -> str:
    return "".join(JP_SHINJITAI_TO_TRADITIONAL.get(ch, ch) for ch in text)


def is_pure_kanji(text: str) -> bool:
    return bool(text) and not KANA_RE.search(text)


def convert_file(filename: str) -> tuple[int, int]:
    path = DATA_DIR / filename
    entries = json.loads(path.read_text(encoding="utf-8"))

    converted, skipped = 0, 0
    for entry in entries:
        if entry.get("source") != "osm":
            continue
        if entry.get("name") != entry.get("name_local"):
            continue  # 已經有中文名稱（例如之前人工/LLM補過），不覆蓋
        name_local = entry.get("name_local", "")
        if not is_pure_kanji(name_local):
            skipped += 1
            continue

        new_name = convert_text(name_local)
        if new_name != entry["name"]:
            print(f"[convert_traditional] {entry['id']}: {entry['name']} -> {new_name}")
            entry["name"] = new_name
            entry["source_note"] = (entry.get("source_note") or "") + "｜name欄位為新字體機械轉繁體，非翻譯"
            converted += 1

    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    return converted, skipped


def main() -> None:
    for filename in ("attractions.json", "hotels.json", "restaurants.json"):
        converted, skipped = convert_file(filename)
        print(f"[convert_traditional] {filename}: 轉換 {converted} 筆，{skipped} 筆含假名跳過（需另外翻譯）")


if __name__ == "__main__":
    main()
