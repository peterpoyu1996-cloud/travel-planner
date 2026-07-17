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
