"""
Trip Input API - Demo Beat 1.

Accepts origin, destination, departure time, and travel mode from an
authenticated user, and stores it as a trip. This is intentionally
minimal: no route segmentation, no risk scoring, no hazard windows.
Those are separate modules, built later, on top of this one.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.db.database import get_db
from app.models.alert import Alert
from app.models.risk_assessment import RiskAssessment
from app.models.route_segment import RouteSegment
from app.models.user import User
from app.models.trip import Trip
from app.schemas.alert import AlertOut
from app.schemas.risk_assessment import RiskAssessmentOut
from app.schemas.route_segment import RouteSegmentOut
from app.schemas.trip import TripCreate, TripOut, TripSnapshotOut

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

@router.get(
    "/{trip_id}/full",
    response_model=TripSnapshotOut,
    summary="Get full trip snapshot (segments, risk assessments, alerts)",
    description="Combined payload for History and Offline Center screens - everything needed to render a trip without extra calls.",
)
def get_trip_snapshot(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TripSnapshotOut:
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if trip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    segments = db.query(RouteSegment).filter(RouteSegment.trip_id == trip_id).all()
    segment_ids = [s.id for s in segments]
    risk_assessments = (
        db.query(RiskAssessment).filter(RiskAssessment.route_segment_id.in_(segment_ids)).all()
        if segment_ids else []
    )
    alerts = db.query(Alert).filter(Alert.trip_id == trip_id).all()

    return TripSnapshotOut(
        trip=TripOut.model_validate(trip),
        segments=[RouteSegmentOut.model_validate(s) for s in segments],
        risk_assessments=[RiskAssessmentOut.model_validate(r) for r in risk_assessments],
        alerts=[AlertOut.model_validate(a) for a in alerts],
    )
