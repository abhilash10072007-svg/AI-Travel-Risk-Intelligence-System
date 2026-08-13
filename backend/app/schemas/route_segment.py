"""
Request/response shapes for route segments - the per-zone breakdown
of a trip (Zone A, B, C, D in the PDF's demo).
"""
from datetime import datetime
from pydantic import BaseModel


class RouteSegmentCreate(BaseModel):
    trip_id: int
    zone_name: str
    rainfall_band: int | None = None
    terrain_band: int | None = None
    flood_history_band: int | None = None
    transport_status: str | None = None
    eta: datetime | None = None


class RouteSegmentOut(BaseModel):
    id: int
    trip_id: int | None = None
    zone_name: str | None = None
    rainfall_band: int | None = None
    terrain_band: int | None = None
    flood_history_band: int | None = None
    transport_status: str | None = None
    eta: datetime | None = None

    model_config = {"from_attributes": True}