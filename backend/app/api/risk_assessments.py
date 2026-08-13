"""
Risk Assessment API - stores the output of the scoring formula.
The actual scoring logic belongs to Nikhil's risk engine; this API
just persists and retrieves whatever it computes.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.risk_assessment import RiskAssessment
from app.schemas.risk_assessment import RiskAssessmentCreate, RiskAssessmentOut

router = APIRouter(prefix="/api/risk-assessments", tags=["risk-assessments"])


@router.post("", response_model=RiskAssessmentOut, summary="Create a risk assessment")
def create_risk_assessment(
    assessment_in: RiskAssessmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RiskAssessment:
    assessment = RiskAssessment(**assessment_in.model_dump())
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@router.get(
    "/by-segment/{route_segment_id}",
    response_model=list[RiskAssessmentOut],
    summary="List risk assessments for a route segment",
)
def list_risk_assessments(
    route_segment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RiskAssessment]:
    return (
        db.query(RiskAssessment)
        .filter(RiskAssessment.route_segment_id == route_segment_id)
        .all()
    )