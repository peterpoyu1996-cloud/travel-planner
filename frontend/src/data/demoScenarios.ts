import type { ItineraryResponse } from '../types'

/**
 * 預先產生的範例情境，直接嵌在前端、不呼叫後端 API（零成本、即點即看）。
 * 內容原則跟 backend/app/demo_fixtures.py 一樣：只用 data/*.json 裡真實存在的候選資料，
 * 資料庫不支援的地方（例如沒有海灘飯店、沒有無障礙標記）誠實寫進 warnings，不硬掰景點。
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
    id: 'couple-car',
    title: '兩人夫妻・開車',
    persona: '5天4夜、有租車、預算 $$',
    emoji: '🚗',
    itinerary: {
      days: [
        {
          day_index: 1,
          date: '2026-09-12',
          stops: [
            { id: 'kokusai-street', name: '國際通', category: 'attraction', reason: '從那霸機場出發順路，兩人可以慢慢逛街買藥妝，時間彈性不趕行程', suggested_stay_duration: null, travel_time_from_prev: null, parking_notes: null, requires_reservation: false },
            { id: 'tomari-fish-market', name: '泊港漁市場', category: 'attraction', reason: '北上前順路安排，感受在地海鮮市場氛圍，適合悠閒散步', suggested_stay_duration: null, travel_time_from_prev: null, parking_notes: '旁邊有停車場', requires_reservation: false },
            { id: 'churaumi-mura-apartment', name: '美麗海村公寓', category: 'hotel', reason: '當晚入住地點，公寓式住宿附餐具，適合想自己簡單開伙的兩人旅行', suggested_stay_duration: null, travel_time_from_prev: '約1.5小時（16:00出發，約17:30到）', parking_notes: null, requires_reservation: true },
          ],
        },
        {
          day_index: 2,
          date: '2026-09-13',
          stops: [
            { id: 'heart-rock', name: '心形岩', category: 'attraction', reason: '北部熱門拍照景點，適合情侶留念，旁邊即有停車場', suggested_stay_duration: null, travel_time_from_prev: null, parking_notes: '旁邊有停車場', requires_reservation: false },
            { id: 'kouri-tower', name: '古宇利塔', category: 'attraction', reason: '與心形岩同區域順路安排，營業時間10:00-18:00內造訪即可', suggested_stay_duration: null, travel_time_from_prev: null, parking_notes: '旁邊有停車場', requires_reservation: false },
            { id: 'kaichukan-observatory', name: '海中觀景塔', category: 'attraction', reason: '含玻璃船行程，兩人可以一起體驗海底景觀，車程約1小時', suggested_stay_duration: null, travel_time_from_prev: '約1小時（8:30出發，約9:30到）', parking_notes: '旁邊有停車場；門票需先在 OTS 買（含玻璃船套票）', requires_reservation: false },
            { id: 'hyakunenkoya-ooya', name: '百年古家 大家 阿古豬', category: 'restaurant', reason: '北部晚餐，兩人份涮涮鍋套餐剛好，記得提前訂位', suggested_stay_duration: null, travel_time_from_prev: '約30分鐘車程', parking_notes: '旁邊有停車場', requires_reservation: true },
          ],
        },
        {
          day_index: 3,
          date: '2026-09-14',
          stops: [
            { id: 'churaumi-aquarium', name: '美麗海水族館', category: 'attraction', reason: '室內展館適合悠閒散步約會，下雨也不受影響，建議走北口停車場', suggested_stay_duration: '約1小時起（依實際規劃可更長）', travel_time_from_prev: null, parking_notes: '在元氣村（海洋博公園）內；停北口停車場，P9停車場進去直走停P7立體停車場', requires_reservation: false },
            { id: 'yakiniku-motobu-bokujo', name: '燒肉本部牧場', category: 'restaurant', reason: '北部晚餐，營業時間17:00-21:30，室內用餐氣氛適合兩人小酌', suggested_stay_duration: null, travel_time_from_prev: null, parking_notes: '旁邊有停車場', requires_reservation: false },
          ],
        },
        {
          day_index: 4,
          date: '2026-09-15',
          stops: [
            { id: 'hamanoya', name: '濱の家', category: 'restaurant', reason: '北部午餐，營業時間約12:10-14:00，離開北部前的最後一餐', suggested_stay_duration: '約12:10到14:00離開', travel_time_from_prev: null, parking_notes: '旁邊有停車場', requires_reservation: false },
            { id: 'ryukyu-no-ushi-chatan', name: '琉球之牛 北谷店', category: 'restaurant', reason: '中部美國村晚餐，晚餐前可以在美國村自由逛街，樓下即有停車場', suggested_stay_duration: null, travel_time_from_prev: null, parking_notes: '樓下有停車場', requires_reservation: false },
          ],
        },
        { day_index: 5, date: '2026-09-16', stops: [] },
      ],
      warnings: [
        '中部白天唯一的候選景點「沖繩兒童王國」是親子取向設施，兩人旅行沒有特別安排；Day4 改成美國村自由活動＋晚餐，若想去也可以自行加入。',
        'Day5（返程日）候選景點已在前4天用完，知識庫在那霸市區白天景點/早午餐選項不足，故意留白不硬湊，建議把當天留給退房、還車、逛機場。',
      ],
    },
  },
  {
    id: 'couple-no-car',
    title: '兩人夫妻・不開車',
    persona: '5天4夜、無租車、預算 $$',
    emoji: '🚌',
    itinerary: {
      days: [
        { day_index: 1, date: '2026-09-12', stops: [
          { id: 'kokusai-street', name: '國際通', category: 'attraction', reason: '知識庫中唯一標記「步行」可達、且不依賴開車的景點，那霸機場出發順路', suggested_stay_duration: null, travel_time_from_prev: null, parking_notes: null, requires_reservation: false },
        ] },
        { day_index: 2, date: '2026-09-13', stops: [] },
        { day_index: 3, date: '2026-09-14', stops: [] },
        { day_index: 4, date: '2026-09-15', stops: [] },
        { day_index: 5, date: '2026-09-16', stops: [] },
      ],
      warnings: [
        '這是刻意呈現的「資料不足」情境：知識庫目前 15 筆資料裡，北部景點與全部 3 間飯店的 travel_mode 都標記「開車」（因為原始資料來源本身全程租車），沒有大眾運輸可達的替代資料，所以無法在不開車的前提下生成完整 5 天行程。',
        '系統選擇誠實留白，而不是硬掰不存在的景點或路線——這正是規則式過濾＋LLM 生成架構要達成的效果：只用候選清單裡真的有的資料。',
        '實務建議（非知識庫景點，僅為一般性建議）：那霸市區可用單軌電車/巴士移動；北部景點建議另外安排一日包車或觀光巴士行程，或考慮短租車 1-2 天。',
        '這也標出了知識庫下一步該補的資料：大眾運輸可達的景點與飯店（尤其是那霸市區），見 docs/ROADMAP.md Phase 1。',
      ],
    },
  },
  {
    id: 'family4-water',
    title: '一家四口・玩水需求',
    persona: '5天4夜、有租車、有帶小孩、想玩水、想住海灘飯店',
    emoji: '🏖️',
    itinerary: {
      days: [
        {
          day_index: 1,
          date: '2026-09-12',
          stops: [
            { id: 'kokusai-street', name: '國際通', category: 'attraction', reason: '抵達當天順路，帶小孩逛街買藥妝，時間彈性', suggested_stay_duration: null, travel_time_from_prev: null, parking_notes: null, requires_reservation: false },
            { id: 'tomari-fish-market', name: '泊港漁市場', category: 'attraction', reason: '北上前順路，小孩可以看新鮮漁獲，體驗市場氛圍', suggested_stay_duration: null, travel_time_from_prev: null, parking_notes: '旁邊有停車場', requires_reservation: false },
            { id: 'churaumi-mura-apartment', name: '美麗海村公寓', category: 'hotel', reason: '知識庫目前最接近北部海岸的住宿候選，公寓式附餐具方便帶小孩自己煮；⚠️ 未確認是否為海灘飯店（見下方提醒）', suggested_stay_duration: null, travel_time_from_prev: '約1.5小時（16:00出發，約17:30到）', parking_notes: null, requires_reservation: true },
          ],
        },
        {
          day_index: 2,
          date: '2026-09-13',
          stops: [
            { id: 'kaichukan-observatory', name: '海中觀景塔', category: 'attraction', reason: '含玻璃船體驗，是知識庫中唯一沾得上「水上活動」邊的候選，小孩會喜歡透過玻璃船看海底', suggested_stay_duration: null, travel_time_from_prev: '約1小時（8:30出發，約9:30到）', parking_notes: '旁邊有停車場；門票需先在 OTS 買（含玻璃船套票）', requires_reservation: false },
            { id: 'heart-rock', name: '心形岩', category: 'attraction', reason: '海邊景點，小孩可以在岸邊玩，順路安排', suggested_stay_duration: null, travel_time_from_prev: null, parking_notes: '旁邊有停車場', requires_reservation: false },
            { id: 'hyakunenkoya-ooya', name: '百年古家 大家 阿古豬', category: 'restaurant', reason: '北部晚餐，涮涮鍋套餐需先預訂，記得提前訂位', suggested_stay_duration: null, travel_time_from_prev: '約30分鐘車程', parking_notes: '旁邊有停車場', requires_reservation: true },
          ],
        },
        {
          day_index: 3,
          date: '2026-09-14',
          stops: [
            { id: 'churaumi-aquarium', name: '美麗海水族館', category: 'attraction', reason: '知識庫明確標記適合親子，室內水族展示是這趟行程「玩水」需求最實際的替代方案，下雨備案也很好用', suggested_stay_duration: '約1小時起（依實際規劃可更長）', travel_time_from_prev: null, parking_notes: '在元氣村（海洋博公園）內；停北口停車場，P9停車場進去直走停P7立體停車場', requires_reservation: false },
            { id: 'yakiniku-motobu-bokujo', name: '燒肉本部牧場', category: 'restaurant', reason: '北部晚餐，室內用餐不受天氣影響', suggested_stay_duration: null, travel_time_from_prev: null, parking_notes: '旁邊有停車場', requires_reservation: false },
          ],
        },
        {
          day_index: 4,
          date: '2026-09-15',
          stops: [
            { id: 'hamanoya', name: '濱の家', category: 'restaurant', reason: '北部午餐，時間較短需抓準（約12:10-14:00）', suggested_stay_duration: '約12:10到14:00離開', travel_time_from_prev: null, parking_notes: '旁邊有停車場', requires_reservation: false },
            { id: 'okinawa-kodomo-no-kuni', name: '沖繩兒童王國', category: 'attraction', reason: '知識庫明確標記適合帶小孩的親子動物園/遊樂設施，建議下午進場停留約1.5小時', suggested_stay_duration: '14:30進場，16:00離開（約1.5小時）', travel_time_from_prev: null, parking_notes: '旁邊有停車場', requires_reservation: false },
            { id: 'ryukyu-no-ushi-chatan', name: '琉球之牛 北谷店', category: 'restaurant', reason: '中部美國村晚餐，營業到22:00時間較彈性', suggested_stay_duration: null, travel_time_from_prev: null, parking_notes: '樓下有停車場', requires_reservation: false },
          ],
        },
        { day_index: 5, date: '2026-09-16', stops: [] },
      ],
      warnings: [
        '⚠️ 知識庫目前沒有任何一筆資料標記「海灘飯店」或「可下水游泳的海灘」，「美麗海村公寓」是地理上最北、最靠近海岸的候選，但沒有實際確認是否鄰近可玩水的沙灘，請視為暫定住宿，出發前務必自行查證。',
        '「玩水」需求目前只能用「美麗海水族館」（室內水族展示）與「海中觀景塔」（玻璃船）替代，兩者都不是實際下水游泳的活動，這是知識庫最大的資料缺口。',
        '下一步建議（見 docs/ROADMAP.md）：補充恩納村/名護沿岸知名海灘度假村資料，才能真正滿足「玩水+住海灘飯店」的需求。',
      ],
    },
  },
  {
    id: 'family6-balance',
    title: '一家六口・老少平衡',
    persona: '5天4夜、有租車、長輩行動不便、小孩想玩水，需要取得平衡',
    emoji: '👵👦',
    itinerary: {
      days: [
        {
          day_index: 1,
          date: '2026-09-12',
          stops: [
            { id: 'kokusai-street', name: '國際通', category: 'attraction', reason: '平面步行街，長輩可自行控制走多久、隨時找地方坐下休息，彈性最高，適合當作抵達日暖身', suggested_stay_duration: null, travel_time_from_prev: null, parking_notes: null, requires_reservation: false },
            { id: 'tomari-fish-market', name: '泊港漁市場', category: 'attraction', reason: '室內市場空間不大，走動距離短，適合全家短暫停留', suggested_stay_duration: null, travel_time_from_prev: null, parking_notes: '旁邊有停車場', requires_reservation: false },
            { id: 'churaumi-mura-apartment', name: '美麗海村公寓', category: 'hotel', reason: '當晚入住地點；⚠️ 知識庫沒有無障礙設施資料，公寓式住宿是否有電梯/是否需爬樓梯請直接向業者確認', suggested_stay_duration: null, travel_time_from_prev: '約1.5小時（16:00出發，約17:30到）', parking_notes: null, requires_reservation: true },
          ],
        },
        {
          day_index: 2,
          date: '2026-09-13',
          stops: [
            { id: 'churaumi-aquarium', name: '美麗海水族館', category: 'attraction', reason: '室內、動線平緩，是全家唯一「老少都適合」的候選：長輩可以坐著看大水槽休息，小孩也能滿足看水生動物的興趣，最接近「玩水」的體驗', suggested_stay_duration: '約1小時起（依實際規劃可更長）', travel_time_from_prev: null, parking_notes: '在元氣村（海洋博公園）內；停北口停車場，P9停車場進去直走停P7立體停車場', requires_reservation: false },
            { id: 'hyakunenkoya-ooya', name: '百年古家 大家 阿古豬', category: 'restaurant', reason: '室內用餐，6人份訂位務必提前打電話確認位子（原資料為2人份套餐，人數需另外確認）', suggested_stay_duration: null, travel_time_from_prev: '約30分鐘車程', parking_notes: '旁邊有停車場', requires_reservation: true },
          ],
        },
        {
          day_index: 3,
          date: '2026-09-14',
          stops: [
            { id: 'okinawa-kodomo-no-kuni', name: '沖繩兒童王國', category: 'attraction', reason: '知識庫標記適合帶小孩；⚠️ 走動範圍較大，建議長輩可在園內休息區等候，年輕家長帶小孩活動，分開行動取得平衡', suggested_stay_duration: '14:30進場，16:00離開（約1.5小時）', travel_time_from_prev: null, parking_notes: '旁邊有停車場', requires_reservation: false },
            { id: 'yakiniku-motobu-bokujo', name: '燒肉本部牧場', category: 'restaurant', reason: '室內用餐，晚餐前特意不排下午行程，讓長輩有休息時間', suggested_stay_duration: null, travel_time_from_prev: null, parking_notes: '旁邊有停車場', requires_reservation: false },
          ],
        },
        {
          day_index: 4,
          date: '2026-09-15',
          stops: [
            { id: 'hamanoya', name: '濱の家', category: 'restaurant', reason: '室內午餐，時間較短需抓準（約12:10-14:00）', suggested_stay_duration: '約12:10到14:00離開', travel_time_from_prev: null, parking_notes: '旁邊有停車場', requires_reservation: false },
            { id: 'ryukyu-no-ushi-chatan', name: '琉球之牛 北谷店', category: 'restaurant', reason: '中部美國村晚餐，營業到22:00時間彈性，不用趕時間', suggested_stay_duration: null, travel_time_from_prev: null, parking_notes: '樓下有停車場', requires_reservation: false },
          ],
        },
        { day_index: 5, date: '2026-09-16', stops: [] },
      ],
      warnings: [
        '⚠️ 知識庫目前完全沒有「無障礙設施」「地面平坦度」這類欄位，以上安排是我依既有欄位（室內外、建議停留時間、分類）保守推測的結果，出發前務必逐一向店家/景點確認實際無障礙動線。',
        '刻意排除了「心形岩」「古宇利塔」：兩者都是戶外海岸礁石地形，行走面不平整，對行動不便的長輩風險較高，知識庫也沒有標記難易度，寧可不排也不要冒險安排。',
        'Day3 故意只排半天行程（上午留白），讓長輩有休息時間——這是刻意的節奏設計，不是資料不足。',
        '下一步建議：知識庫應新增「無障礙／步行難易度」欄位，這類多世代同行的情境才能規劃得更準確，見 docs/ROADMAP.md。',
      ],
    },
  },
]
