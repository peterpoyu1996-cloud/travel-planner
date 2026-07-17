"""StaticDemoProvider 用的示範行程內容。

這不是隨機編造的假資料：是針對 data/*.json 目前真實候選清單（見
scraper/merge_osm.py 執行後的結果），依 itinerary.py 的 SYSTEM_PROMPT 規則
人工推演一次的結果，用來在沒有 ANTHROPIC_API_KEY 時，也能跑通
filters → itinerary → frontend 整條管線。

範例條件：2026-08-01 ~ 2026-08-05、住美麗海村公寓、有租車、有帶小孩(國小)、預算 $$。
"""

DEMO_ITINERARY_RESPONSE_JSON = """
{
  "days": [
    {
      "day_index": 1,
      "date": "2026-08-01",
      "stops": [
        {
          "id": "kokusai-street",
          "name": "國際通",
          "category": "attraction",
          "reason": "從那霸機場出發順路，可逛街買藥妝、去牧志市場吃飯糰當早餐，屬彈性時段不影響後續行程",
          "suggested_stay_duration": null,
          "travel_time_from_prev": null,
          "parking_notes": null,
          "requires_reservation": false
        },
        {
          "id": "tomari-fish-market",
          "name": "泊港漁市場",
          "category": "attraction",
          "reason": "那霸市區內、北上前順路安排，旁邊有停車場，體驗當地海鮮氛圍",
          "suggested_stay_duration": null,
          "travel_time_from_prev": null,
          "parking_notes": "旁邊有停車場",
          "requires_reservation": false
        },
        {
          "id": "churaumi-mura-apartment",
          "name": "美麗海村公寓",
          "category": "hotel",
          "reason": "當晚入住地點，公寓式住宿附餐具與煮飯器具，若想簡單開伙很方便；從那霸出發車程約1.5小時",
          "suggested_stay_duration": null,
          "travel_time_from_prev": "約1.5小時（16:00出發，約17:30到）",
          "parking_notes": null,
          "requires_reservation": true
        }
      ]
    },
    {
      "day_index": 2,
      "date": "2026-08-02",
      "stops": [
        {
          "id": "heart-rock",
          "name": "心形岩",
          "category": "attraction",
          "reason": "北部知名景點，旁邊即有停車場，適合與古宇利塔排在同一天",
          "suggested_stay_duration": null,
          "travel_time_from_prev": null,
          "parking_notes": "旁邊有停車場",
          "requires_reservation": false
        },
        {
          "id": "kouri-tower",
          "name": "古宇利塔",
          "category": "attraction",
          "reason": "與心形岩在同一區域，順路安排，營業時間10:00-18:00內造訪即可",
          "suggested_stay_duration": null,
          "travel_time_from_prev": null,
          "parking_notes": "旁邊有停車場",
          "requires_reservation": false
        },
        {
          "id": "kaichukan-observatory",
          "name": "海中觀景塔",
          "category": "attraction",
          "reason": "與前兩站同在北部路線上，車程約1小時，室內外展區皆有，下雨也能室內部分參觀",
          "suggested_stay_duration": null,
          "travel_time_from_prev": "約1小時（8:30出發，約9:30到）",
          "parking_notes": "旁邊有停車場；門票需先在 OTS 買（含玻璃船套票）",
          "requires_reservation": false
        },
        {
          "id": "hyakunenkoya-ooya",
          "name": "百年古家 大家 阿古豬",
          "category": "restaurant",
          "reason": "北部晚餐選擇，涮涮鍋套餐需先預訂，記得提前訂位",
          "suggested_stay_duration": null,
          "travel_time_from_prev": "約30分鐘車程",
          "parking_notes": "旁邊有停車場",
          "requires_reservation": true
        }
      ]
    },
    {
      "day_index": 3,
      "date": "2026-08-03",
      "stops": [
        {
          "id": "churaumi-aquarium",
          "name": "美麗海水族館",
          "category": "attraction",
          "reason": "室內展館，知識庫已標記適合親子，也是雨天備案的好選擇；在海洋博公園內，建議走北口停車場",
          "suggested_stay_duration": "約1小時起（依實際規劃可更長）",
          "travel_time_from_prev": null,
          "parking_notes": "在元氣村（海洋博公園）內；停北口停車場，P9停車場進去直走停P7立體停車場",
          "requires_reservation": false
        },
        {
          "id": "yakiniku-motobu-bokujo",
          "name": "燒肉本部牧場",
          "category": "restaurant",
          "reason": "北部晚餐，營業時間17:00-21:30，室內用餐不受天氣影響",
          "suggested_stay_duration": null,
          "travel_time_from_prev": null,
          "parking_notes": "旁邊有停車場",
          "requires_reservation": false
        }
      ]
    },
    {
      "day_index": 4,
      "date": "2026-08-04",
      "stops": [
        {
          "id": "hamanoya",
          "name": "濱の家",
          "category": "restaurant",
          "reason": "北部午餐，營業時間約12:10-14:00，時間較短需抓準",
          "suggested_stay_duration": "約12:10到14:00離開",
          "travel_time_from_prev": null,
          "parking_notes": "旁邊有停車場",
          "requires_reservation": false
        },
        {
          "id": "okinawa-kodomo-no-kuni",
          "name": "沖繩兒童王國",
          "category": "attraction",
          "reason": "中部親子景點，知識庫明確標記適合帶小孩，建議下午進場停留約1.5小時，營業至17:30",
          "suggested_stay_duration": "14:30進場，16:00離開（約1.5小時）",
          "travel_time_from_prev": null,
          "parking_notes": "旁邊有停車場",
          "requires_reservation": false
        },
        {
          "id": "ryukyu-no-ushi-chatan",
          "name": "琉球之牛 北谷店",
          "category": "restaurant",
          "reason": "中部美國村晚餐，樓下即有停車場，營業到22:00時間較彈性",
          "suggested_stay_duration": null,
          "travel_time_from_prev": null,
          "parking_notes": "樓下有停車場",
          "requires_reservation": false
        }
      ]
    },
    {
      "day_index": 5,
      "date": "2026-08-05",
      "stops": []
    }
  ],
  "warnings": [
    "Day5（最後一天/返程日）候選景點已在前 4 天用完，剩下唯一未使用的候選「暖暮拉麵」17:00才開門，不適合安排在通常需要提早退房、還車、趕飛機的返程日，因此本日故意留白，而不是硬塞不合適的行程。知識庫目前在「那霸市區/瀨長島一帶的白天景點與早午餐選項」明顯不足，建議之後爬蟲/人工補這塊。",
    "「美麗海水族館」目前缺少確切營業時間資料（opening_hours為null），建議去之前先查證，避免撲空。",
    "知識庫中另有「那霸日航都市飯店」「琉球溫泉 瀨長島飯店」兩筆飯店候選，但本次行程已指定住宿地為「美麗海村公寓」，故未使用，僅供你未來規劃其他住宿方案參考。"
  ]
}
"""
