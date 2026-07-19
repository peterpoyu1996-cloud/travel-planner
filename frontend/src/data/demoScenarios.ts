import type { ItineraryResponse } from '../types'

/**
 * 預先產生的範例情境，直接嵌在前端、不呼叫後端 API（零成本、即點即看）。
 *
 * 這裡刻意放兩種不同來源的範例，供對照比較：
 * - `family3-south-to-north`（id 是 data/*.json 裡真實存在的候選 id）：本專案系統產出，
 *   只用知識庫真實候選資料，travel_time_from_prev 是用 common/geo/travel_time.py 針對每筆候選
 *   的真實座標實際算出來的（平面道路 vs 高速公路，取比較快的一條），資料庫不支援的地方
 *   （例如飯店是否緊鄰沙灘、餐廳平日不供應午餐）誠實寫進 warnings，不硬掰景點。
 * - `chat-raw-comparison`（id 一律用 `chat-` 前綴，不對應知識庫任何真實候選）：同一個 prompt
 *   直接丟給 Claude Chat（沒有知識庫、沒有即時查證）得到的原始回答，逐字轉錄，車程/景點名稱
 *   都未經過座標驗證，只用來跟上面那個範例並排比較「有沒有真實資料支撐」的差異。
 */

export interface DemoScenario {
  id: string
  title: string
  persona: string
  emoji: string
  itinerary: ItineraryResponse
}

export const DEMO_SCENARIOS: DemoScenario[] = [
  {
    id: 'family3-south-to-north',
    title: '兩大一小(6歲)・南玩到北再回來',
    persona: '5天4夜、有租車自駕、含國際通/海灘飯店/水族館/購物中心/動物園/燒肉',
    emoji: '🚗',
    itinerary: {
      days: [
        {
          day_index: 1,
          date: '2026-09-12',
          stops: [
            { id: 'kokusai-street', name: '國際通', category: 'attraction', reason: '從那霸機場租車出發順路，先讓小孩下車活動、逛街買藥妝，開店時間彈性不趕行程', suggested_stay_duration: null, travel_time_from_prev: null, parking_notes: null, requires_reservation: false },
            { id: 'osm-attr-1068043305', name: '首里城公園', category: 'attraction', reason: '南部代表性世界遺產景點，官網查證過營業時間隨季節調整、停車場收費方式（小型車60分500日圓），方便抓時間', suggested_stay_duration: null, travel_time_from_prev: '約6分鐘（平面道路直線距離約3.6km（含繞路係數））', parking_notes: '小型車60分500日圓，之後每30分250日圓，最高1000日圓；身心障礙手冊持有者免費；停車時間限3小時內', requires_reservation: false },
            { id: 'osm-rest-4489395093', name: '燒肉本舗 島牛', category: 'restaurant', reason: '南部晚餐燒肉，OSM資料顯示營業到凌晨（11:30-14:00,17:00-24:00），不用趕打烊時間', suggested_stay_duration: null, travel_time_from_prev: '約6分鐘（平面道路直線距離約3.4km（含繞路係數））', parking_notes: null, requires_reservation: false },
            { id: 'osm-hotel-5010880558', name: 'Smile飯店那霸城市度假村', category: 'hotel', reason: '第一晚住宿，鄰近國際通與今晚燒肉店，晚餐後直接回房休息；⚠️知識庫目前沒有這間飯店的親子設施資料，訂房前建議自行確認', suggested_stay_duration: null, travel_time_from_prev: '約2分鐘（平面道路直線距離約0.8km（含繞路係數））', parking_notes: null, requires_reservation: true },
          ],
        },
        {
          day_index: 2,
          date: '2026-09-13',
          stops: [
            { id: 'aeon-mall-okinawa-rycom', name: 'AEON MALL沖繩來客夢', category: 'attraction', reason: '中部大型購物中心，官網查證過地址與MapCode（33 530 406*45），室內逛街不受天氣影響，離動物園只要3分鐘', suggested_stay_duration: null, travel_time_from_prev: '約19分鐘（經那覇IC上、喜舎場スマートIC下，高速公路段13.0km）', parking_notes: '大型購物中心附設停車場', requires_reservation: false },
            { id: 'okinawa-kodomo-no-kuni', name: '沖繩兒童王國', category: 'attraction', reason: '知識庫明確標記適合帶小孩，營業時間9:30-17:30，緊鄰購物中心順路安排', suggested_stay_duration: null, travel_time_from_prev: '約3分鐘（平面道路直線距離約1.7km（含繞路係數））', parking_notes: '旁邊有停車場', requires_reservation: false },
            { id: 'osm-hotel-2676267351', name: '蒙特雷飯店沖繩 溫泉度假村', category: 'hotel', reason: '今晚海灘飯店，位於恩納村西海岸；⚠️知識庫沒有這間飯店是否緊鄰沙灘的確切資料，訂房前建議自行查證', suggested_stay_duration: null, travel_time_from_prev: '約17分鐘（經沖縄南IC上、石川IC下，高速公路段14.6km）', parking_notes: null, requires_reservation: true },
          ],
        },
        {
          day_index: 3,
          date: '2026-09-14',
          stops: [
            { id: 'churaumi-aquarium', name: '美麗海水族館', category: 'attraction', reason: '北部必訪水族館，官網查證過MapCode與停車場動線（P9停車場進去直走停P7），知識庫標記適合親子', suggested_stay_duration: '約1小時起（依實際規劃可更長）', travel_time_from_prev: '約48分鐘（平面道路直線距離約27.7km（含繞路係數））', parking_notes: '在元氣村（海洋博公園）內；停北口停車場，P9停車場進去直走停P7立體停車場', requires_reservation: false },
            { id: 'yakiniku-motobu-bokujo', name: '燒肉本部牧場', category: 'restaurant', reason: '北部晚餐燒肉，官網查證過營業時間17:00-21:30與MapCode，室內用餐不受天氣影響', suggested_stay_duration: null, travel_time_from_prev: '約7分鐘（平面道路直線距離約4.1km（含繞路係數））', parking_notes: '旁邊有停車場', requires_reservation: false },
            { id: 'osm-hotel-7923784018', name: 'Hilton Okinawa Sesoko Resort', category: 'hotel', reason: '今晚第二晚海灘飯店，緊鄰水族館與晚餐燒肉店，車程都在10分鐘內；⚠️知識庫沒有這間飯店的親子設施資料，訂房前建議自行確認', suggested_stay_duration: null, travel_time_from_prev: '約5分鐘（平面道路直線距離約2.8km（含繞路係數））', parking_notes: null, requires_reservation: true },
          ],
        },
        {
          day_index: 4,
          date: '2026-09-15',
          stops: [
            { id: 'osm-rest-13730263900', name: '燒肉食堂 Kouya', category: 'restaurant', reason: '回程午餐，中部順路點；⚠️OSM營業時間資料顯示平日只有17:00-23:00營業，只有週末/國定假日才有中午12:00場，行前務必依實際出發日期確認', suggested_stay_duration: null, travel_time_from_prev: '約56分鐘（經許田IC上、中城PA下，高速公路段46.3km）', parking_notes: null, requires_reservation: false },
            { id: 'kokusai-street', name: '國際通', category: 'attraction', reason: '回程第二次造訪，這次專門安排伴手禮採購時間，商店多、營業時間彈性', suggested_stay_duration: null, travel_time_from_prev: '約15分鐘（經中城PA上、那覇IC下，高速公路段10.2km）', parking_notes: null, requires_reservation: false },
            { id: 'osm-hotel-1583677053', name: '東橫INN那霸新都心Omoromachi', category: 'hotel', reason: '最後一晚住宿，鄰近機場方便隔天還車搭機', suggested_stay_duration: null, travel_time_from_prev: '約3分鐘（平面道路直線距離約1.8km（含繞路係數））', parking_notes: null, requires_reservation: true },
          ],
        },
        { day_index: 5, date: '2026-09-16', stops: [] },
      ],
      warnings: [
        '第4天午餐候選「燒肉食堂 Kouya」平日只有17:00後營業，只有週末/國定假日中午12:00才開，如果實際出發日落在平日，這一餐需要改選其他午餐地點，不要照抄本範例硬排。',
        '兩晚海灘飯店（蒙特雷飯店沖繩溫泉度假村、Hilton Okinawa Sesoko Resort）知識庫來源都是 OSM，只有名稱座標，沒有親子設施/是否緊鄰沙灘等資料，訂房前請自行向業者確認。',
        'Day5（返程日）刻意留白：候選清單這趟已排滿5天所需的景點/餐廳/飯店，且知識庫沒有機場周邊的晨間備案資料，返程日通常要退房、加油還車、抓時間到機場，寧可留白讓你彈性運用，不硬塞行程。',
      ],
    },
  },
  {
    id: 'chat-raw-comparison',
    title: 'Claude Chat 直接生成（比較用）',
    persona: '同一個 prompt，未使用知識庫/未經座標查證，逐字轉錄',
    emoji: '💬',
    itinerary: {
      days: [
        {
          day_index: 1,
          date: '2026-09-12',
          stops: [
            { id: 'chat-naha-airport', name: '那霸機場', category: 'logistics', reason: '07:00抵達、入境領行李；07:00-08:00機場內簡易早餐；08:00搭租車公司接駁車前往取車處；09:00完成手續正式開始自駕', suggested_stay_duration: '07:00-09:00', travel_time_from_prev: null, parking_notes: null, requires_reservation: false },
            { id: 'chat-kokusai-street', name: '國際通', category: 'attraction', reason: '逛街、牧志公設市場、藥妝伴手禮；12:00-13:00於周邊吃沖繩麵當午餐；下午繼續壺屋通散策', suggested_stay_duration: '09:20-14:20', travel_time_from_prev: '車程約15-20分（約5km）', parking_notes: null, requires_reservation: false },
            { id: 'chat-nanbu-beach-hotel', name: '瀬長島/豐崎海灘度假飯店', category: 'hotel', reason: 'check-in、戲水放鬆（未指定確切飯店名稱，「補充提醒」建議可考慮「琉球溫泉 瀬長島ホテル」或豐崎一帶親子飯店）', suggested_stay_duration: '15:00 check-in', travel_time_from_prev: '車程約20分（約8km）', parking_notes: null, requires_reservation: false },
            { id: 'chat-yakiniku-day1', name: '燒肉（飯店周邊燒肉店）', category: 'restaurant', reason: '晚餐燒肉（未指定確切店名）；19:00後可安排瀬長島夕陽/自由活動', suggested_stay_duration: '17:30-18:30', travel_time_from_prev: null, parking_notes: null, requires_reservation: false },
          ],
        },
        {
          day_index: 2,
          date: '2026-09-13',
          stops: [
            { id: 'chat-kodomo-no-kuni', name: '沖繩こどもの国（動物園）', category: 'attraction', reason: '退房後前往，適合6歲小孩參觀；12:00-13:00於沖繩市內用餐', suggested_stay_duration: '09:30-12:00', travel_time_from_prev: '車程約50分，走那霸空港道+沖繩道，約35km', parking_notes: null, requires_reservation: false },
            { id: 'chat-american-village', name: '美國村', category: 'attraction', reason: '逛街、摩天輪、海邊拍照', suggested_stay_duration: '13:30-15:30', travel_time_from_prev: '車程約20-25分（約15km）', parking_notes: null, requires_reservation: false },
            { id: 'chat-hokubu-beach-resort', name: '北部海灘度假飯店（建議部瀬名岬一帶）', category: 'hotel', reason: '連住兩晚，隔天不用搬行李（未指定確切飯店名稱，「補充提醒」建議可考慮部瀬名岬周邊度假村，如The Busena Terrace同等級酒店）；晚餐於飯店內或周邊', suggested_stay_duration: '16:30 check-in、17:30-18:30晚餐', travel_time_from_prev: '車程約50-60分（約40km）', parking_notes: null, requires_reservation: false },
          ],
        },
        {
          day_index: 3,
          date: '2026-09-14',
          stops: [
            { id: 'chat-churaumi-aquarium', name: '沖繩美麗海水族館（海洋博公園）', category: 'attraction', reason: '建議一開館就進場避開人潮；接續海豚劇場、翡翠海灘、熱帶夢幻中心；12:00-13:00於海洋博公園美食街用餐', suggested_stay_duration: '09:10-15:30', travel_time_from_prev: '車程約30-40分（約25km）', parking_notes: null, requires_reservation: false },
            { id: 'chat-hokubu-beach-resort', name: '北部海灘度假飯店（連住第2晚）', category: 'hotel', reason: '回飯店泳池/海灘戲水，晚餐於飯店內，早點休息', suggested_stay_duration: '16:00起、17:30-18:30晚餐', travel_time_from_prev: '車程約30-40分', parking_notes: null, requires_reservation: false },
          ],
        },
        {
          day_index: 4,
          date: '2026-09-15',
          stops: [
            { id: 'chat-aeon-rycom', name: 'AEON MALL沖繩來客夢（Rycom）', category: 'attraction', reason: '退房後出發，沖繩最大購物中心，設施完善適合親子；12:00-13:00於mall美食街用餐，下午繼續購物、伴手禮採買', suggested_stay_duration: '09:45-15:30', travel_time_from_prev: '車程約60-70分（約55km，走沖繩道）', parking_notes: null, requires_reservation: false },
            { id: 'chat-naha-city-hotel', name: '那霸市區飯店', category: 'hotel', reason: 'check-in（未指定確切飯店名稱）', suggested_stay_duration: '16:00 check-in', travel_time_from_prev: '車程約20-30分（約15km）', parking_notes: null, requires_reservation: false },
            { id: 'chat-yakiniku-day4', name: '燒肉（那霸市區）', category: 'restaurant', reason: '晚餐燒肉（未指定確切店名）；19:00後可再逛一次國際通夜景', suggested_stay_duration: '17:30-18:30', travel_time_from_prev: null, parking_notes: null, requires_reservation: false },
          ],
        },
        {
          day_index: 5,
          date: '2026-09-16',
          stops: [
            { id: 'chat-outlet-ashibinaa', name: 'Outlet Mall Ashibinaa', category: 'attraction', reason: '退房後前往最後採買', suggested_stay_duration: '09:00-11:00', travel_time_from_prev: '車程約20分（約10km）', parking_notes: null, requires_reservation: false },
            { id: 'chat-naha-airport-return', name: '那霸機場（還車/登機）', category: 'logistics', reason: '還車、接駁車前往航廈；機場內午餐後辦理登機準備搭機', suggested_stay_duration: '11:00-13:00後', travel_time_from_prev: '車程約15-20分（約8km）', parking_notes: null, requires_reservation: false },
          ],
        },
      ],
      warnings: [
        '⚠️ 此範例逐字轉錄自另一次對話中 Claude Chat 對同一個 prompt 的直接回答：沒有使用本專案知識庫，景點/飯店名稱、座標、車程分鐘數都未經過查證或實際計算，僅供跟「兩大一小・南玩到北再回來」範例（知識庫真實候選＋高速公路網路實際計算）並排比較用，不建議直接照抄出發。',
        '原始回答中 Day1/Day2/Day4 的飯店與燒肉店都只給了地區/等級建議（例如「瀬長島/豐崎海灘度假飯店」「北部海灘度假飯店（建議部瀬名岬一帶）」），沒有指定實際存在、可訂房的單一飯店名稱。',
        '住宿建議（原文）：Day1南部可考慮「琉球溫泉 瀬長島ホテル」或豐崎一帶親子飯店；Day2-3北部可考慮部瀬名岬周邊度假村（如The Busena Terrace同等級酒店），連住2晚省去搬行李。',
        '租車提醒（原文）：6歲小孩建議加租兒童安全座椅，日本法規強制規定6歲以下需使用。',
        '車程提醒（原文）：沖繩自動車道雖然要收費，但能省下不少時間，建議全程走高速再接一般道路；車程皆為預估值，實際會因路況、租車地點稍有差異，出發前建議用Google Maps再次確認即時路況。',
      ],
    },
  },
]
