from datetime import date, time

from pydantic import BaseModel, Field, model_validator


class TripConditions(BaseModel):
    start_date: date
    end_date: date
    lodging: str
    has_car: bool
    has_kids: bool
    kid_age_range: str | None = None
    budget_level: str  # "$" | "$$" | "$$$"
    start_location: str


class ItineraryStop(BaseModel):
    id: str
    name: str
    category: str
    reason: str
    suggested_stay_duration: str | None = None
    travel_time_from_prev: str | None = None
    parking_notes: str | None = None
    requires_reservation: bool = False
    eta: time | None = None  # 實際時鐘到達時間，只有分天規劃且該天有時間窗時才會算
    must_arrive_by: time | None = None  # 使用者標的訂位時間，沒標就是 None
    late_by_minutes: float | None = None  # 有值代表這站會遲到（排不進時間窗），不是 0 就是真的晚了


class DayPlan(BaseModel):
    day_index: int
    date: date
    stops: list[ItineraryStop]


class ItineraryResponse(BaseModel):
    days: list[DayPlan]
    warnings: list[str] = []


class GeoAnchor(BaseModel):
    """自訂路線的起點/終點：既有知識庫 POI（重用它的座標）或明確座標（例如機場、
    知識庫沒收錄的地標）擇一，不能兩者都給或都不給。
    """

    poi_id: str | None = None
    lat: float | None = None
    lng: float | None = None
    label: str | None = None  # 沒有 poi_id 時，顯示用的名稱

    @model_validator(mode="after")
    def _exactly_one_source(self) -> "GeoAnchor":
        has_poi = self.poi_id is not None
        has_coords = self.lat is not None and self.lng is not None
        if has_poi == has_coords:
            raise ValueError("GeoAnchor 需要 poi_id 或 (lat, lng) 擇一，不能兩者都給或都不給")
        return self


class CustomRouteRequest(BaseModel):
    """使用者自訂景點清單 → 最小車程排序。跟 TripConditions（LLM 生成）刻意分開，
    這條路徑不經過 LLM，順序由 common/geo/route_optimizer.py 演算法算出來。
    """

    attraction_ids: list[str] = Field(..., min_length=1, max_length=30)  # 硬上限在 schema 層執行
    trip_days: int = Field(..., ge=1, le=14)
    start_date: date  # 用來算每個 DayPlan.date，跟 TripConditions.start_date 同精神
    start: GeoAnchor
    end: GeoAnchor | None = None


class CustomRouteResponse(BaseModel):
    days: list[DayPlan]
    warnings: list[str] = []
    total_travel_minutes: float
    excluded_attraction_ids: list[str] = []  # 因缺座標被排除的 id，誠實回報，不是靜默丟棄


class DayStopInput(BaseModel):
    """分天規劃裡的單一景點，多數景點 must_arrive_by 都是 None（自由排序）——只有
    使用者自己標「這個有訂位」的少數幾個景點才會填時間。只有上限（幾點前要到），
    沒有下限（太早到不算錯，那是使用者自己判斷要不要多逛一下）。
    """

    attraction_id: str
    must_arrive_by: time | None = None


class DayBucket(BaseModel):
    """使用者自己指定「這一天要去這幾個景點」，不限地區——地區只是前端瀏覽用的
    篩選器，不是資料上的硬規則（見跟使用者的討論：中部玩一玩、傍晚往北部飯店移動
    這種安排，靠真實經緯度算車程本來就會自然反映，不需要靠地區標籤去限制）。

    start_time 是這天的出發時鐘時間，只有在這天有景點標了 must_arrive_by 時才有意義
    （沒有時間窗的天，出發時間不影響排序結果，純粹是相對車程加總）。
    """

    stops: list[DayStopInput] = Field(..., min_length=1, max_length=15)
    start_time: time = time(9, 0)


class DayPlanRequest(BaseModel):
    """使用者自己分天選好景點，程式負責：1) 幫每天內部景點排最佳順序（有訂位時間的
    景點會盡量排到不遲到，真的排不下會老實回報，不會生一個實際上會遲到的行程）
    2) 檢查天序（哪天先去）順不順，不順的話建議更好的天序（只調換天的順序，
    不會把使用者選的景點搬到別天）。跟 CustomRouteRequest 的差異見
    common/geo/route_optimizer.py 的 evaluate_day_plan() 開頭說明。
    """

    days: list[DayBucket] = Field(..., min_length=1, max_length=7)  # 上限見 route_optimizer.MAX_DAY_PLAN_DAYS
    start_date: date
    start: GeoAnchor
    end: GeoAnchor | None = None

    @model_validator(mode="after")
    def _total_attraction_cap(self) -> "DayPlanRequest":
        total = sum(len(day.stops) for day in self.days)
        if total > 30:
            raise ValueError(f"景點總數（{total}）超過上限 30 筆")

        all_ids = [stop.attraction_id for day in self.days for stop in day.stops]
        dupes = sorted({i for i in all_ids if all_ids.count(i) > 1})
        if dupes:
            raise ValueError(f"同一個景點不能安排在多天：{', '.join(dupes)}")
        return self


class DayPlanResponse(BaseModel):
    chosen_days: list[DayPlan]
    chosen_total_minutes: float
    suggested_order: list[int] | None = None  # 對應 request.days 的索引排列；None 代表使用者選的天序已經最好
    suggested_days: list[DayPlan] | None = None
    suggested_total_minutes: float | None = None
    minutes_saved: float = 0.0
    warnings: list[str] = []
    excluded_attraction_ids: list[str] = []
