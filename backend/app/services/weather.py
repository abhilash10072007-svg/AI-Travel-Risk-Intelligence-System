"""
Fetches live rainfall data from Open-Meteo (free, no API key) and
converts it to the IMD-style band (1-5) used by the scoring formula.

This does NOT replace the static route_segments data model - it only
supplies a real rainfall_band value instead of a guessed one. Terrain
and flood-history bands remain static, since they're geographic facts,
not weather.
"""
import httpx

# Approximate coordinates for each zone along the Coimbatore-Palakkad corridor.
# Zone A/D are near the endpoints; B/C are along the ghat section (NH544).
ZONE_COORDINATES = {
    "Zone A": (11.0168, 76.9558),   # Coimbatore
    "Zone B": (10.9500, 76.8500),   # midpoint
    "Zone C": (10.8500, 76.7500),   # ghat section - historically highest risk
    "Zone D": (10.7867, 76.6548),   # Palakkad
}


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


def fetch_current_rainfall_band(zone_name: str) -> int:
    """
    Fetches live current precipitation for a zone and converts it to
    a rainfall_band (1-5). Falls back to band 1 (no data) on any
    network/API failure, so a live demo never crashes on this.
    """
    coords = ZONE_COORDINATES.get(zone_name)
    if coords is None:
        return 1

    lat, lon = coords
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
        mm_per_hour = data.get("current", {}).get("precipitation", 0)
        return rainfall_mm_to_band(mm_per_hour)
    except Exception:
        # Network failure, API down, etc. - never let this break the demo.
        return 1