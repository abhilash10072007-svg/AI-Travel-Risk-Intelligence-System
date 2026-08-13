from fastapi import APIRouter
from pydantic import BaseModel

from services.weather_service import fetch_current_rainfall_band
from services.riskengine import calculate_risk


router = APIRouter()


class RiskRequest(BaseModel):
    zone: str
    weather: str
    terrain: str


@router.post("/risk")
def get_risk(data: RiskRequest):

    rainfall_band = fetch_current_rainfall_band(
        data.zone
    )

    result = calculate_risk(
        rainfall_band,
        data.weather,
        data.terrain
    )

    return result