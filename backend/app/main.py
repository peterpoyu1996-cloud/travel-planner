from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .itinerary import generate_itinerary
from .models import ItineraryResponse, TripConditions

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
