"""
Route Segment API - per-zone breakdown of a trip.
Minimal CRUD for now; the actual segmentation logic (splitting a trip
into zones automatically) is a separate, later module.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.route_segment import RouteSegment
from app.schemas.route_segment import RouteSegmentCreate, RouteSegmentOut
from app.services.weather import fetch_current_rainfall_band

router = APIRouter(prefix="/api/route-segments", tags=["route-segments"])


@router.post("", response_model=RouteSegmentOut, summary="Create a route segment")
def create_route_segment(
    segment_in: RouteSegmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RouteSegment:
    segment = RouteSegment(**segment_in.model_dump())
    db.add(segment)
    db.commit()
    db.refresh(segment)
    return segment


@router.get("/by-trip/{trip_id}", response_model=list[RouteSegmentOut], summary="List segments for a trip")
def list_route_segments(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RouteSegment]:
    return db.query(RouteSegment).filter(RouteSegment.trip_id == trip_id).all()

# Static geographic data per zone - terrain and flood history don't
# change hour to hour, so these stay fixed (matches the PDF's worked example).
ZONE_STATIC_DATA = {
    "Zone A": {"terrain_band": 2, "flood_history_band": 2, "transport_status": "Normal"},
    "Zone B": {"terrain_band": 3, "flood_history_band": 3, "transport_status": "Normal"},
    "Zone C": {"terrain_band": 5, "flood_history_band": 3, "transport_status": "Normal"},  # ghat section
    "Zone D": {"terrain_band": 2, "flood_history_band": 2, "transport_status": "Normal"},
}


@router.post(
    "/seed-for-trip/{trip_id}",
    response_model=list[RouteSegmentOut],
    summary="Seed the 4 demo zones for a trip using live rainfall data",
    description="Creates Zone A-D for the given trip. Rainfall is fetched live from Open-Meteo; terrain and flood-history are static.",
)
def seed_route_segments_for_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RouteSegment]:
    created = []
    for zone_name, static_data in ZONE_STATIC_DATA.items():
        rainfall_band = fetch_current_rainfall_band(zone_name)
        segment = RouteSegment(
            trip_id=trip_id,
            zone_name=zone_name,
            rainfall_band=rainfall_band,
            terrain_band=static_data["terrain_band"],
            flood_history_band=static_data["flood_history_band"],
            transport_status=static_data["transport_status"],
        )
        db.add(segment)
        created.append(segment)
    db.commit()
    for segment in created:
        db.refresh(segment)
    return created