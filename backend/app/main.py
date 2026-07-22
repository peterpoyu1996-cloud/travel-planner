from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .custom_route import generate_custom_route
from .day_plan import generate_day_plan
from .itinerary import generate_itinerary
from .models import (
    CustomRouteRequest,
    CustomRouteResponse,
    DayPlanRequest,
    DayPlanResponse,
    ItineraryResponse,
    TripConditions,
)
from .poi_catalog import PublicPOI, list_public_pois

app = FastAPI(title="旅遊決策助手 API（沖繩試點）")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite 預設開發埠
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/itinerary", response_model=ItineraryResponse)
def create_itinerary(conditions: TripConditions) -> ItineraryResponse:
    try:
        return generate_itinerary(conditions)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/attractions", response_model=list[PublicPOI])
def get_attractions() -> list[PublicPOI]:
    return list_public_pois()


@app.post("/custom-route", response_model=CustomRouteResponse)
def create_custom_route(request: CustomRouteRequest) -> CustomRouteResponse:
    try:
        return generate_custom_route(request)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/day-plan", response_model=DayPlanResponse)
def create_day_plan(request: DayPlanRequest) -> DayPlanResponse:
    try:
        return generate_day_plan(request)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
