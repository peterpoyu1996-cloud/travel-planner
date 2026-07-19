"""StaticDemoProvider 用的示範行程內容。

這不是隨機編造的假資料：是針對 data/*.json 目前真實候選清單，依 itinerary.py 的
SYSTEM_PROMPT 規則人工推演一次的結果，用來在沒有 ANTHROPIC_API_KEY 時，也能跑通
filters → itinerary → frontend 整條管線。travel_time_from_prev 的數字是用
common/geo/travel_time.py 針對每筆候選的真實座標實際算出來的（會被
itinerary.fill_real_travel_times() 用真實候選清單再覆蓋一次，兩邊算法相同，
數字應該一致）。

範例條件：2026-09-12 ~ 2026-09-16、兩大一小(6歲)、有租車，南部進、北部折返，
含國際通/海灘飯店/美麗海水族館/購物中心/動物園/燒肉，五天四夜。
"""

DEMO_ITINERARY_RESPONSE_JSON = """
{
  "days": [
    {
      "day_index": 1,
      "date": "2026-09-12",
      "stops": [
        {
          "id": "kokusai-street",
          "name": "國際通",
          "category": "attraction",
          "reason": "從那霸機場租車出發順路，先讓小孩下車活動、逛街買藥妝，開店時間彈性不趕行程",
          "suggested_stay_duration": null,
          "travel_time_from_prev": null,
          "parking_notes": null,
          "requires_reservation": false
        },
        {
          "id": "osm-attr-1068043305",
          "name": "首里城公園",
          "category": "attraction",
          "reason": "南部代表性世界遺產景點，官網查證過營業時間隨季節調整、停車場收費方式（小型車60分500日圓），方便抓時間",
          "suggested_stay_duration": null,
          "travel_time_from_prev": "約6分鐘（平面道路直線距離約3.6km（含繞路係數））",
          "parking_notes": "小型車60分500日圓，之後每30分250日圓，最高1000日圓；身心障礙手冊持有者免費；停車時間限3小時內",
          "requires_reservation": false
        },
        {
          "id": "osm-rest-4489395093",
          "name": "燒肉本舗 島牛",
          "category": "restaurant",
          "reason": "南部晚餐燒肉，OSM資料顯示營業到凌晨（11:30-14:00,17:00-24:00），不用趕打烊時間",
          "suggested_stay_duration": null,
          "travel_time_from_prev": "約6分鐘（平面道路直線距離約3.4km（含繞路係數））",
          "parking_notes": null,
          "requires_reservation": false
        },
        {
          "id": "osm-hotel-5010880558",
          "name": "Smile飯店那霸城市度假村",
          "category": "hotel",
          "reason": "第一晚住宿，鄰近國際通與今晚燒肉店，晚餐後直接回房休息；⚠️知識庫目前沒有這間飯店的親子設施資料，訂房前建議自行確認",
          "suggested_stay_duration": null,
          "travel_time_from_prev": "約2分鐘（平面道路直線距離約0.8km（含繞路係數））",
          "parking_notes": null,
          "requires_reservation": true
        }
      ]
    },
    {
      "day_index": 2,
      "date": "2026-09-13",
      "stops": [
        {
          "id": "aeon-mall-okinawa-rycom",
          "name": "AEON MALL沖繩來客夢",
          "category": "attraction",
          "reason": "中部大型購物中心，官網查證過地址與MapCode（33 530 406*45），室內逛街不受天氣影響，離動物園只要3分鐘",
          "suggested_stay_duration": null,
          "travel_time_from_prev": "約19分鐘（經那覇IC上、喜舎場スマートIC下，高速公路段13.0km）",
          "parking_notes": "大型購物中心附設停車場",
          "requires_reservation": false
        },
        {
          "id": "okinawa-kodomo-no-kuni",
          "name": "沖繩兒童王國",
          "category": "attraction",
          "reason": "知識庫明確標記適合帶小孩，營業時間9:30-17:30，緊鄰購物中心順路安排",
          "suggested_stay_duration": null,
          "travel_time_from_prev": "約3分鐘（平面道路直線距離約1.7km（含繞路係數））",
          "parking_notes": "旁邊有停車場",
          "requires_reservation": false
        },
        {
          "id": "osm-hotel-2676267351",
          "name": "蒙特雷飯店沖繩 溫泉度假村",
          "category": "hotel",
          "reason": "今晚海灘飯店，位於恩納村西海岸；⚠️知識庫沒有這間飯店是否緊鄰沙灘的確切資料，訂房前建議自行查證",
          "suggested_stay_duration": null,
          "travel_time_from_prev": "約17分鐘（經沖縄南IC上、石川IC下，高速公路段14.6km）",
          "parking_notes": null,
          "requires_reservation": true
        }
      ]
    },
    {
      "day_index": 3,
      "date": "2026-09-14",
      "stops": [
        {
          "id": "churaumi-aquarium",
          "name": "美麗海水族館",
          "category": "attraction",
          "reason": "北部必訪水族館，官網查證過MapCode與停車場動線（P9停車場進去直走停P7），知識庫標記適合親子",
          "suggested_stay_duration": "約1小時起（依實際規劃可更長）",
          "travel_time_from_prev": "約48分鐘（平面道路直線距離約27.7km（含繞路係數））",
          "parking_notes": "在元氣村（海洋博公園）內；停北口停車場，P9停車場進去直走停P7立體停車場",
          "requires_reservation": false
        },
        {
          "id": "yakiniku-motobu-bokujo",
          "name": "燒肉本部牧場",
          "category": "restaurant",
          "reason": "北部晚餐燒肉，官網查證過營業時間17:00-21:30與MapCode，室內用餐不受天氣影響",
          "suggested_stay_duration": null,
          "travel_time_from_prev": "約7分鐘（平面道路直線距離約4.1km（含繞路係數））",
          "parking_notes": "旁邊有停車場",
          "requires_reservation": false
        },
        {
          "id": "osm-hotel-7923784018",
          "name": "Hilton Okinawa Sesoko Resort",
          "category": "hotel",
          "reason": "今晚第二晚海灘飯店，緊鄰水族館與晚餐燒肉店，車程都在10分鐘內；⚠️知識庫沒有這間飯店的親子設施資料，訂房前建議自行確認",
          "suggested_stay_duration": null,
          "travel_time_from_prev": "約5分鐘（平面道路直線距離約2.8km（含繞路係數））",
          "parking_notes": null,
          "requires_reservation": true
        }
      ]
    },
    {
      "day_index": 4,
      "date": "2026-09-15",
      "stops": [
        {
          "id": "osm-rest-13730263900",
          "name": "燒肉食堂 Kouya",
          "category": "restaurant",
          "reason": "回程午餐，中部順路點；⚠️OSM營業時間資料顯示平日只有17:00-23:00營業，只有週末/國定假日才有中午12:00場，行前務必依實際出發日期確認",
          "suggested_stay_duration": null,
          "travel_time_from_prev": "約56分鐘（經許田IC上、中城PA下，高速公路段46.3km）",
          "parking_notes": null,
          "requires_reservation": false
        },
        {
          "id": "kokusai-street",
          "name": "國際通",
          "category": "attraction",
          "reason": "回程第二次造訪，這次專門安排伴手禮採購時間，商店多、營業時間彈性",
          "suggested_stay_duration": null,
          "travel_time_from_prev": "約15分鐘（經中城PA上、那覇IC下，高速公路段10.2km）",
          "parking_notes": null,
          "requires_reservation": false
        },
        {
          "id": "osm-hotel-1583677053",
          "name": "東橫INN那霸新都心Omoromachi",
          "category": "hotel",
          "reason": "最後一晚住宿，鄰近機場方便隔天還車搭機",
          "suggested_stay_duration": null,
          "travel_time_from_prev": "約3分鐘（平面道路直線距離約1.8km（含繞路係數））",
          "parking_notes": null,
          "requires_reservation": true
        }
      ]
    },
    {
      "day_index": 5,
      "date": "2026-09-16",
      "stops": []
    }
  ],
  "warnings": [
    "第4天午餐候選「燒肉食堂 Kouya」平日只有17:00後營業，只有週末/國定假日中午12:00才開，如果實際出發日落在平日，這一餐需要改選其他午餐地點，不要照抄本範例硬排。",
    "兩晚海灘飯店（蒙特雷飯店沖繩溫泉度假村、Hilton Okinawa Sesoko Resort）知識庫來源都是 OSM，只有名稱座標，沒有親子設施/是否緊鄰沙灘等資料，訂房前請自行向業者確認。",
    "Day5（返程日）刻意留白：候選清單這趟已排滿5天所需的景點/餐廳/飯店，且知識庫沒有機場周邊的晨間備案資料，返程日通常要退房、加油還車、抓時間到機場，寧可留白讓你彈性運用，不硬塞行程。"
  ]
}
"""
