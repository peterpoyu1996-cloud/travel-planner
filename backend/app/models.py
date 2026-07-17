from datetime import date

from pydantic import BaseModel


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


class DayPlan(BaseModel):
    day_index: int
    date: date
    stops: list[ItineraryStop]


class ItineraryResponse(BaseModel):
    days: list[DayPlan]
    warnings: list[str] = []
