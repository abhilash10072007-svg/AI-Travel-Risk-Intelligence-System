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