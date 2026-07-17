"""把含假名（片假名/平假名）的 OSM 條目名稱翻成繁體中文。

跟 convert_traditional.py 不同：那支是機械式字元替換（新字體→繁體，語意不變，
零風險）；這支是「真的翻譯」，需要語意判斷，有出錯風險。

原則：只翻我有把握的（知名連鎖店、有廣泛紀錄的知名景點、或是單純的通用外來語
組合，例如「ホテル」=飯店、「ビーチ」=海灘），翻譯後在 source_note 誠實標註
「LLM輔助翻譯」，不是機械轉換也不是官方譯名。

沒把握的（在地小吃店、沖繩方言詞彙，例如「ぶくぶく」「なかゆくい」這種），
寧可保留日文原名不硬翻，避免翻錯誤導使用者，等之後有更可靠的資料來源
（例如官網有繁中版本）再補。這是刻意的取捨，不是漏做。
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# id -> 翻譯後的繁體中文名稱，只收錄有把握的
CONFIDENT_TRANSLATIONS = {
    "osm-attr-1068014185": "沖繩世界 玉泉洞",
    "osm-attr-602895164": "姬百合和平祈念資料館",
    "osm-attr-5076211521": "國際海洋資訊中心",
    "osm-attr-1068016179": "埋藏文化財中心",
    "osm-attr-13340657801": "沖繩便便博物館",
    "osm-attr-13740236877": "虛擬博物館",
    "osm-attr-5885009907": "伊江海灘",
    "osm-attr-1068010664": "東南植物樂園",
    "osm-attr-1068028521": "國營沖繩紀念公園熱帶亞熱帶都市綠化植物園",
    "osm-attr-1993614054": "果報崖",
    "osm-rest-11214895437": "串炸田中",
    "osm-rest-13716549922": "Royal Host",
    "osm-rest-13021137193": "金澤まいもん壽司",
    "osm-rest-4330713892": "岸本食堂",
    "osm-rest-12876542801": "Jolly Pasta 名護店",
    "osm-rest-1995215744": "曙光便當",
    "osm-rest-2883289307": "天空食堂",
    "osm-rest-1995215770": "中本天婦羅店",
    "osm-rest-4780279222": "山之茶屋・樂水",
    "osm-hotel-1583677053": "東橫INN那霸新都心Omoromachi",
    "osm-hotel-2676267351": "蒙特雷飯店沖繩 溫泉度假村",
    "osm-hotel-5010880558": "Smile飯店那霸城市度假村",
}


def apply_translations(filename: str) -> int:
    path = DATA_DIR / filename
    entries = json.loads(path.read_text(encoding="utf-8"))

    count = 0
    for entry in entries:
        translation = CONFIDENT_TRANSLATIONS.get(entry["id"])
        if translation and entry.get("name") == entry.get("name_local"):
            print(f"[translate_names] {entry['id']}: {entry['name_local']} -> {translation}")
            entry["name"] = translation
            entry["source_note"] = (entry.get("source_note") or "") + "｜name欄位為LLM輔助翻譯，非官方譯名，如不準確請協助修正"
            count += 1

    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    return count


def main() -> None:
    total = 0
    for filename in ("attractions.json", "hotels.json", "restaurants.json"):
        total += apply_translations(filename)
    print(f"[translate_names] 共翻譯 {total} 筆。其餘含假名但沒把握的名稱維持日文原名，"
          f"見 data/schema.md「資料現況」的說明。")


if __name__ == "__main__":
    main()
