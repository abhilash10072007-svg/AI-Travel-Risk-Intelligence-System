"""
Request/response shapes for Journey Guardian alerts.
"""
from datetime import datetime
from pydantic import BaseModel


class AlertCreate(BaseModel):
    trip_id: int
    alert_type: str
    message: str | None = None


class AlertOut(BaseModel):
    id: int
    trip_id: int | None = None
    alert_type: str | None = None
    message: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}