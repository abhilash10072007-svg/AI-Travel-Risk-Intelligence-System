"""
Alert API - Journey Guardian notifications.
The detection/trigger logic belongs to the Journey Guardian module;
this API just persists and retrieves alerts.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertOut

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.post("", response_model=AlertOut, summary="Create an alert")
def create_alert(
    alert_in: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Alert:
    alert = Alert(**alert_in.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.get("/by-trip/{trip_id}", response_model=list[AlertOut], summary="List alerts for a trip")
def list_alerts(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Alert]:
    return db.query(Alert).filter(Alert.trip_id == trip_id).all()