"""
Trip Input API - Demo Beat 1.

Accepts origin, destination, departure time, and travel mode from an
authenticated user, and stores it as a trip. This is intentionally
minimal: no route segmentation, no risk scoring, no hazard windows.
Those are separate modules, built later, on top of this one.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.trip import Trip
from app.schemas.trip import TripCreate, TripOut

router = APIRouter(prefix="/api/trips", tags=["trips"])


@router.post(
    "",
    response_model=TripOut,
    summary="Create a trip",
    description="Requires a valid Firebase ID token. Creates a trip owned by the authenticated user.",
)
def create_trip(
    trip_in: TripCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Trip:
    trip = Trip(
        user_id=current_user.id,
        origin=trip_in.origin,
        destination=trip_in.destination,
        departure_time=trip_in.departure_time,
        travel_mode=trip_in.travel_mode,
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@router.get(
    "",
    response_model=list[TripOut],
    summary="List the current user's trips",
    description="Requires a valid Firebase ID token. Returns only trips owned by the authenticated user.",
)
def list_trips(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Trip]:
    return (
        db.query(Trip)
        .filter(Trip.user_id == current_user.id)
        .order_by(Trip.created_at.desc())
        .all()
    )