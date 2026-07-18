"""新增 `translated_name` 欄位：把 name_local 的中文翻譯結果放這裡，
跟 `name`（目前顯示用的「有把握」名稱）分開，不互相污染。

規則：
- `name` 本來就是中文（不管是 excel_seed、機械轉換、LLM高信心翻譯、還是OSM社群標籤）：
  `translated_name` = `name`，兩欄位一樣
- `name` 目前還是日文（含假名/方言，之前刻意沒翻，怕翻錯誤導使用者）：
  現在補上 LLM 翻譯結果到 `translated_name`，但 `name` 保持原樣不動——
  這樣可以在 UI 用 translated_name 顯示中文，同時保留「這則是不是原本就
  很確定」的訊號（比較 name 是否等於 name_local 就知道）

這批翻譯是 LLM 輔助、非官方譯名，尤其沖繩方言詞彙（バンタ、ゆいまーる、
ぶくぶく 這類）是音譯兼意譯，不保證跟當地慣用譯名一致，已在 source_note 註記。
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# id -> 翻譯，只收錄之前 name==name_local 且含假名、還沒翻過的條目
BEST_EFFORT_TRANSLATIONS = {
    # attractions
    "osm-attr-11936491418": "清海農場",
    "osm-attr-11384600037": "安須杜健行步道",
    "osm-attr-5325219237": "沖繩市戰後文化資料展示室 Histreet",
    "osm-attr-8226624094": "沖繩市音樂資料館 音樂村",
    "osm-attr-1068017752": "宇流麻市立石川歷史民俗資料館",
    "osm-attr-1068032145": "東村立山與水生活博物館",
    "osm-attr-1068038865": "宇流麻市立海洋文化資料館",
    "osm-attr-2002204635": "美背福木林道",
    "osm-attr-2004299632": "Helios酒造",
    "osm-attr-5885017123": "迷你馬",
    "osm-attr-11215905557": "海與丘展望台",
    "osm-attr-13021850942": "恐龍探索樂園",
    "osm-attr-1563212509": "西展望台",
    "osm-attr-1717637950": "安保瞭望之丘",
    "osm-attr-1993614062": "悠閒歇腳處（那卡由庫伊）",
    # hotels
    "osm-hotel-1583677055": "Almont飯店",
    "osm-hotel-4673553180": "北方Yuimaru本館",
    "osm-hotel-4742180621": "413濱比嘉 Hotel & Cafe",
    "osm-hotel-5885046890": "Star House小屋",
    "osm-hotel-6522173518": "Y's CABIN&HOTEL 那霸國際通",
    "osm-hotel-7244186054": "Kaeru-ya 純住宿民宿",
    "osm-hotel-7244193426": "Fuuran 古民家民宿",
    "osm-hotel-11109431705": "Cocktail Stay那霸飯店",
    "osm-hotel-11847179923": "神谷莊（歐吉桑留下的民宿）",
    "osm-hotel-11936431830": "LAC宇流麻（HAMACHŪ內）",
    "osm-hotel-11936431929": "Tripshot Villas・濱比嘉",
    "osm-hotel-11936431959": "The Stella・濱比嘉",
    "osm-hotel-12008683880": "歌聲民宿Māminā",
    "osm-hotel-12008911491": "Ernesto殘波",
    "osm-hotel-12047299673": "Grand Style沖繩 讀谷飯店&度假村",
    "osm-hotel-12056711144": "讀谷公寓飯店ND",
    "osm-hotel-12060293526": "Blue Steak Wonder 瀨名波 沖繩讀谷",
    "osm-hotel-12071200750": "沖繩讀谷 設計師公寓飯店",
    "osm-hotel-12181223789": "Coral Garden Seven Pools",
    "osm-hotel-12243159695": "Avian海濱小屋",
    # restaurants
    "osm-rest-1995215764": "海濱得來速餐廳",
    "osm-rest-4402466094": "隨時吃早餐 本店",
    "osm-rest-5413612723": "Noricce",
    "osm-rest-10573155101": "中華料理 喜悅家",
    "osm-rest-11390871235": "支那蕎麥麵 嘉手苅",
    "osm-rest-11679566966": "Mike's Hanbi店",
    "osm-rest-11936431766": "古民家食堂 Tiirabui",
    "osm-rest-12069082796": "石窯披薩酒場 Maruki",
    "osm-rest-12202937521": "YOMITAN魔女咖哩 惠庵",
    "osm-rest-12715681091": "彩虹咖啡 Nijiiro Cafe",
    "osm-rest-12872439918": "拉麵暖暮 北谷砂邊店",
    "osm-rest-12903832035": "座喜味蕎麥麵",
    "osm-rest-13022143808": "Airando Fiji Cafe（斐濟島咖啡）",
    "osm-rest-13390966851": "拉麵札幌屋",
    "osm-rest-13700547516": "金月蕎麥麵讀谷本店",
    "osm-rest-13730263900": "燒肉食堂 Kouya",
    "osm-rest-1995215734": "名護曲餐廳",
    "osm-rest-1995215757": "Mosugu蕎麥麵 Kunnadu",
    "osm-rest-3792759951": "Suumanumee",
    "osm-rest-4330706892": "Ohacorte",
    "osm-rest-4751048522": "On the Beach咖啡",
    "osm-rest-4846870521": "麵家Nirai",
    "osm-rest-5157158921": "沖繩茶屋 Bukubuku",
}


def process_file(filename: str) -> tuple[int, int]:
    path = DATA_DIR / filename
    entries = json.loads(path.read_text(encoding="utf-8"))

    already_zh, newly_translated = 0, 0
    for entry in entries:
        if entry["id"] in BEST_EFFORT_TRANSLATIONS:
            entry["translated_name"] = BEST_EFFORT_TRANSLATIONS[entry["id"]]
            entry["source_note"] = (entry.get("source_note") or "") + "｜translated_name為LLM輔助翻譯（含沖繩方言音譯），非官方譯名"
            newly_translated += 1
        else:
            entry["translated_name"] = entry["name"]
            already_zh += 1

    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    return already_zh, newly_translated


def main() -> None:
    for filename in ("attractions.json", "hotels.json", "restaurants.json"):
        already_zh, newly_translated = process_file(filename)
        print(f"[add_translated_name] {filename}: {already_zh} 筆沿用name，{newly_translated} 筆新翻譯")


if __name__ == "__main__":
    main()
