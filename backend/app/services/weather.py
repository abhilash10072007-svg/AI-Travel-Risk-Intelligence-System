import httpx


ZONE_COORDINATES = {
    "Zone A": (11.0168, 76.9558),
    "Zone B": (10.9500, 76.8500),
    "Zone C": (10.8500, 76.7500),
    "Zone D": (10.7867, 76.6548),
}


def rainfall_mm_to_band(mm_per_hour: float) -> int:

    if mm_per_hour <= 0:
        return 1

    if mm_per_hour <= 7.5:
        return 2

    if mm_per_hour <= 35.5:
        return 3

    if mm_per_hour <= 64.4:
        return 4

    return 5


def fetch_current_rainfall_band(zone_name: str) -> int:

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

        mm_per_hour = data.get(
            "current", {}
        ).get(
            "precipitation", 0
        )

        return rainfall_mm_to_band(mm_per_hour)

    except Exception:
        return 1