# → Abhilash (API response shapes)

"""
Response shape for /api/auth/me. Only fields safe to return to the client.
"""
from datetime import datetime
from pydantic import BaseModel


class UserOut(BaseModel):
    id: int
    firebase_uid: str | None = None
    email: str | None = None
    name: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}