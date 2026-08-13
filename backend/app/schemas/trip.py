"""
Request/response shapes for the Trip Input API.
Matches Demo Beat 1: origin, destination, departure time, travel mode.
"""
from datetime import datetime
from pydantic import BaseModel


class TripCreate(BaseModel):
    """What the frontend sends to create a trip."""
    origin: str
    destination: str
    departure_time: datetime
    travel_mode: str


class TripOut(BaseModel):
    """What the API returns for a trip."""
    id: int
    user_id: int | None = None
    origin: str | None = None
    destination: str | None = None
    departure_time: datetime | None = None
    travel_mode: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}