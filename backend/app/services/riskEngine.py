# risk_engine.py


def rainfall_score(rainfall_band):

    if rainfall_band == 1:
        return 0

    elif rainfall_band == 2:
        return 10

    elif rainfall_band == 3:
        return 25

    elif rainfall_band == 4:
        return 40

    elif rainfall_band == 5:
        return 50

    else:
        return 0


def weather_score(weather):
    """
    Calculate risk points based on weather condition.
    """

    weather = weather.lower()

    if weather == "clear":
        return 0

    elif weather == "cloudy":
        return 5

    elif weather == "light rain":
        return 10

    elif weather == "heavy rain":
        return 20

    elif weather == "thunderstorm":
        return 25

    else:
        return 0


def terrain_score(terrain):
    """
    Calculate risk points based on terrain.
    """

    terrain = terrain.lower()

    if terrain == "flat":
        return 0

    elif terrain == "undulating":
        return 10

    elif terrain == "hilly":
        return 20

    elif terrain == "steep":
        return 30

    else:
        return 0


def interaction_score(rainfall_band, weather, terrain):

    score = 0

    # High / very high rainfall + hilly terrain
    if rainfall_band >= 4 and terrain.lower() in ["hilly", "steep"]:
        score += 15

    # Very heavy rainfall + steep terrain
    if rainfall_band == 5 and terrain.lower() == "steep":
        score += 20

    # Thunderstorm + high rainfall
    if rainfall_band >= 4 and weather.lower() == "thunderstorm":
        score += 15

    return score



def calculate_risk(rainfall_band, weather, terrain):

    rain_points = rainfall_score(rainfall_band)

    weather_points = weather_score(weather)

    terrain_points = terrain_score(terrain)

    interaction_points = interaction_score(
        rainfall_band,
        weather,
        terrain
    )

    total_score = (
        rain_points
        + weather_points
        + terrain_points
        + interaction_points
    )

    if total_score < 30:
        risk_level = "GREEN"

    elif total_score < 60:
        risk_level = "YELLOW"

    else:
        risk_level = "RED"

    return {
        "rainfall_score": rain_points,
        "weather_score": weather_points,
        "terrain_score": terrain_points,
        "interaction_score": interaction_points,
        "total_score": total_score,
        "risk_level": risk_level
    }


def detect_terrain_type(location_name: str) -> str:
    """
    Automatically infers terrain classification for Tamil Nadu regions
    so a normal user doesn't need to specify technical terrain types.
    """
    name = (location_name or "").strip().lower()

    if any(k in name for k in ["ooty", "kodaikanal", "valparai", "zone c", "ghat"]):
        return "steep"
    elif any(k in name for k in ["nilgiris", "yercaud", "coonoor", "bodimettu", "kolli"]):
        return "hilly"
    elif any(k in name for k in ["palakkad", "pollachi", "zone b", "dindigul", "hosur"]):
        return "undulating"
    else:
        return "flat"


def generate_user_advisory(total_score: int, risk_level: str, weather: str, terrain: str) -> str:
    """
    Generates easy-to-understand, plain-English travel advisory for normal users.
    """
    if risk_level == "GREEN":
        return "Safe travel conditions ahead. Enjoy your journey!"
    elif risk_level == "YELLOW":
        if "rain" in weather.lower() or "drizzle" in weather.lower():
            return f"Caution: Wet roads and {terrain} terrain detected. Drive slowly and keep safe braking distance."
        return f"Moderate travel risk detected due to {terrain} terrain. Drive carefully."
    else:  # RED
        if "thunderstorm" in weather.lower() or "heavy rain" in weather.lower():
            return "Severe hazard warning! Heavy rainfall and harsh weather on steep roads. Delay non-essential travel if possible."
        return "High risk route conditions! Landslide/flooding potential on hilly roads. Drive with extreme caution."