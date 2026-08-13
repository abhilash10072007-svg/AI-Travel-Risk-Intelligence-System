"""
Fetches live rainfall data from Open-Meteo (free, no API key) and
converts it to the IMD-style band (1-5) used by the scoring formula.

Supports:
1. Direct (latitude, longitude) coordinates.
2. Dynamic location names across Tamil Nadu (and all of India) via Open-Meteo Geocoding API.
3. Fast lookup dictionary for all major Tamil Nadu districts & cities.
"""
import httpx
from typing import Optional, Tuple

# Predefined coordinates for major Tamil Nadu districts, cities, and corridor zones.
TAMIL_NADU_COORDINATES = {
    # Demo Corridor Zones (Coimbatore - Palakkad NH544)
    "Zone A": (11.0168, 76.9558),   # Coimbatore
    "Zone B": (10.9500, 76.8500),   # Midpoint
    "Zone C": (10.8500, 76.7500),   # Ghat section (High risk)
    "Zone D": (10.7867, 76.6548),   # Palakkad border

    # Major Tamil Nadu Districts & Cities
    "Chennai": (13.0827, 80.2707),
    "Coimbatore": (11.0168, 76.9558),
    "Madurai": (9.9252, 78.1198),
    "Tiruchirappalli": (10.7905, 78.7047),
    "Trichy": (10.7905, 78.7047),
    "Salem": (11.6643, 78.1460),
    "Tirunelveli": (8.7139, 77.7567),
    "Erode": (11.3410, 77.7172),
    "Vellore": (12.9165, 79.1325),
    "Thanjavur": (10.7870, 79.1378),
    "Dindigul": (10.3673, 77.9803),
    "Kanchipuram": (12.8342, 79.7036),
    "Nilgiris": (11.4102, 76.6950),
    "Ooty": (11.4102, 76.6950),
    "Cuddalore": (11.7480, 79.7714),
    "Nagapattinam": (10.7673, 79.8427),
    "Kanyakumari": (8.0883, 77.5385),
    "Tiruppur": (11.1085, 77.3411),
    "Karur": (10.9601, 78.0766),
    "Ramanathapuram": (9.3639, 78.8395),
    "Hosur": (12.7409, 77.8253),
    "Tuticorin": (8.7642, 78.1348),
    "Thoothukudi": (8.7642, 78.1348),
    "Kodaikanal": (10.2381, 77.4892),
}

# Kept for backward compatibility
ZONE_COORDINATES = TAMIL_NADU_COORDINATES


def rainfall_mm_to_band(mm_per_hour: float) -> int:
    """
    Converts rainfall intensity (mm/hr) to a 1-5 band, using standard
    IMD rainfall intensity classification.
    """
    if mm_per_hour <= 0:
        return 1  # No rain
    if mm_per_hour <= 7.5:
        return 2  # Light rain
    if mm_per_hour <= 35.5:
        return 3  # Moderate rain
    if mm_per_hour <= 64.4:
        return 4  # Heavy rain
    return 5  # Very heavy rain


def geocode_location(location_name: str) -> Optional[Tuple[float, float]]:
    """
    Resolves a location string to (latitude, longitude) coordinates.
    Checks static dictionary first, then falls back to Open-Meteo Geocoding API.
    """
    cleaned_name = location_name.strip()
    
    # 1. Check static dictionary match
    for key, coords in TAMIL_NADU_COORDINATES.items():
        if cleaned_name.lower() == key.lower():
            return coords

    # 2. Dynamic lookup via Open-Meteo free Geocoding API
    try:
        response = httpx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": cleaned_name, "count": 1, "language": "en", "format": "json"},
            timeout=4.0,
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("results")
        if results and len(results) > 0:
            return float(results[0]["latitude"]), float(results[0]["longitude"])
    except Exception:
        pass

    return None


def fetch_current_rainfall_band_by_coords(lat: float, lon: float) -> int:
    """
    Fetches live precipitation for any exact (latitude, longitude) coordinate
    across Tamil Nadu or globally, returning an IMD rainfall band (1-5).
    """
    try:
        response = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "precipitation",
            },
            timeout=5.0,
        )
        response.raise_for_status()
        data = response.json()
        mm_per_hour = data.get("current", {}).get("precipitation", 0.0)
        return rainfall_mm_to_band(mm_per_hour)
    except Exception:
        # Fallback to band 1 (no rain/data) on API timeout or error
        return 1


def wmo_code_to_description(code: int) -> str:
    """Translates WMO Weather Interpretation Codes to human readable text."""
    mapping = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        95: "Thunderstorm",
        96: "Thunderstorm with light hail",
        99: "Thunderstorm with heavy hail",
    }
    return mapping.get(code, "Cloudy / Variable")


def fetch_live_weather_details(zone_or_location: str) -> dict:
    """
    Fetches rich real-time weather data for any city or location in Tamil Nadu.
    Returns precipitation (mm/hr), temperature (°C), humidity (%), wind speed (km/h),
    weather condition description, and IMD rainfall band (1-5).
    """
    coords = geocode_location(zone_or_location)
    if coords is None:
        return {
            "location": zone_or_location,
            "error": "Location not found",
            "rainfall_band": 1,
        }

    lat, lon = coords
    try:
        response = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "precipitation,temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
            },
            timeout=5.0,
        )
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})

        precip = current.get("precipitation", 0.0)
        temp = current.get("temperature_2m", 0.0)
        humidity = current.get("relative_humidity_2m", 0)
        wind_speed = current.get("wind_speed_10m", 0.0)
        code = current.get("weather_code", 0)

        return {
            "location": zone_or_location,
            "latitude": lat,
            "longitude": lon,
            "temperature_c": temp,
            "precipitation_mm_hr": precip,
            "humidity_percent": humidity,
            "wind_speed_kmh": wind_speed,
            "weather_code": code,
            "condition": wmo_code_to_description(code),
            "rainfall_band": rainfall_mm_to_band(precip),
        }
    except Exception as exc:
        return {
            "location": zone_or_location,
            "latitude": lat,
            "longitude": lon,
            "error": str(exc),
            "rainfall_band": 1,
        }


def fetch_current_rainfall_band(zone_or_location: str) -> int:
    """
    Fetches live current precipitation for a zone or location name across Tamil Nadu,
    and converts it to a rainfall_band (1-5).
    """
    coords = geocode_location(zone_or_location)
    if coords is None:
        return 1
    lat, lon = coords
    return fetch_current_rainfall_band_by_coords(lat, lon)