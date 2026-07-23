export type BudgetLevel = '$' | '$$' | '$$$'

export interface TripConditions {
  start_date: string // YYYY-MM-DD
  end_date: string
  lodging: string
  has_car: boolean
  has_kids: boolean
  kid_age_range: string | null
  budget_level: BudgetLevel
  start_location: string
}

export interface ItineraryStop {
  id: string
  name: string
  category: string
  reason: string
  suggested_stay_duration: string | null
  travel_time_from_prev: string | null
  parking_notes: string | null
  requires_reservation: boolean
  eta: string | null // "HH:MM"，只有分天規劃且該天有時間窗時才會有值
  must_arrive_by: string | null // "HH:MM"，使用者標的訂位時間
  late_by_minutes: number | null // 有值代表這站會遲到（排不進時間窗）
}

export interface DayPlan {
  day_index: number
  date: string
  stops: ItineraryStop[]
}

export interface ItineraryResponse {
  days: DayPlan[]
  warnings: string[]
}

export interface PublicPOI {
  id: string
  name: string
  category: string
  region_group: string | null
  sub_area: string | null
  lat: number | null
  lng: number | null
  suggested_stay_duration: string | null
  kid_friendly: number | null
  recommendation_score: number | null
  budget_level: string | null
}

export interface GeoAnchor {
  poi_id?: string | null
  lat?: number | null
  lng?: number | null
  label?: string | null
}

export interface CustomRouteRequest {
  attraction_ids: string[]
  trip_days: number
  start_date: string // YYYY-MM-DD
  start: GeoAnchor
  end?: GeoAnchor | null
}

export interface CustomRouteResponse extends ItineraryResponse {
  total_travel_minutes: number
  excluded_attraction_ids: string[]
}

export interface DayStopInput {
  attraction_id: string
  must_arrive_by?: string | null // "HH:MM"，只有訂位的景點才填，其他留 null
}

export interface DayBucket {
  stops: DayStopInput[]
  start_time?: string // "HH:MM"，這天的出發時間，不給後端預設 09:00
}

export interface DayPlanRequest {
  days: DayBucket[]
  start_date: string // YYYY-MM-DD
  start: GeoAnchor
  end?: GeoAnchor | null
}

export interface DayPlanResponse {
  chosen_days: DayPlan[]
  chosen_total_minutes: number
  suggested_order: number[] | null
  suggested_days: DayPlan[] | null
  suggested_total_minutes: number | null
  minutes_saved: number
  warnings: string[]
  excluded_attraction_ids: string[]
}
