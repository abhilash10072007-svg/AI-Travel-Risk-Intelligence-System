from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.services.weather import fetch_current_rainfall_band, fetch_live_weather_details
from app.services.riskEngine import calculate_risk, detect_terrain_type, generate_user_advisory

router = APIRouter(prefix="/api/risk-engine", tags=["risk-engine"])


class RiskRequest(BaseModel):
    zone: str
    weather: Optional[str] = None
    terrain: Optional[str] = None


class QuickAssessRequest(BaseModel):
    location: str


@router.post("", summary="Calculate risk score using Nikhil's Risk Engine")
def get_risk(data: RiskRequest):
    # Fetch live rainfall band for the zone
    rainfall_band = fetch_current_rainfall_band(data.zone)

    # If weather text is not provided, fetch current weather condition live
    weather_text = data.weather
    if not weather_text:
        live_details = fetch_live_weather_details(data.zone)
        weather_text = live_details.get("condition", "clear")

    terrain_val = data.terrain or detect_terrain_type(data.zone)

    result = calculate_risk(
        rainfall_band=rainfall_band,
        weather=weather_text,
        terrain=terrain_val
    )

    result["zone"] = data.zone
    result["live_weather_condition"] = weather_text
    result["rainfall_band"] = rainfall_band
    result["terrain"] = terrain_val
    result["advisory"] = generate_user_advisory(
        result["total_score"], result["risk_level"], weather_text, terrain_val
    )
    return result


@router.post("/quick-assess", summary="Easy one-click location risk assessment for normal users")
def quick_assess(data: QuickAssessRequest):
    """
    User enters any city or location in Tamil Nadu (e.g. 'Ooty', 'Chennai', 'Madurai').
    System automatically resolves coordinates, fetches real-time weather, infers terrain,
    runs Nikhil's Risk Engine, and returns a plain English advisory.
    """
    location = data.location.strip()
    live_details = fetch_live_weather_details(location)

    if "error" in live_details and live_details["error"] == "Location not found":
        return {"error": f"Location '{location}' not found. Please try another city or zone name."}

    rainfall_band = live_details.get("rainfall_band", 1)
    weather_text = live_details.get("condition", "Clear sky")
    terrain_val = detect_terrain_type(location)

    risk_result = calculate_risk(
        rainfall_band=rainfall_band,
        weather=weather_text,
        terrain=terrain_val
    )

    advisory = generate_user_advisory(
        risk_result["total_score"], risk_result["risk_level"], weather_text, terrain_val
    )

    return {
        "location": location,
        "temperature_c": live_details.get("temperature_c"),
        "weather_condition": weather_text,
        "rainfall_band": rainfall_band,
        "terrain_type": terrain_type_label(terrain_val),
        "total_risk_score": risk_result["total_score"],
        "risk_level": risk_result["risk_level"],
        "advisory": advisory,
        "breakdown": {
            "rain_points": risk_result["rainfall_score"],
            "weather_points": risk_result["weather_score"],
            "terrain_points": risk_result["terrain_score"],
            "interaction_points": risk_result["interaction_score"],
        }
    }


def terrain_type_label(terrain_val: str) -> str:
    labels = {
        "flat": "Flat Plains",
        "undulating": "Undulating / Rolling Hills",
        "hilly": "Hilly / Mountainous",
        "steep": "Steep Ghat Section"
    }
    return labels.get(terrain_val.lower(), terrain_val.title())