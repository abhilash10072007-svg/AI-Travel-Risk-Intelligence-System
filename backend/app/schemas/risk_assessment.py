"""
Request/response shapes for risk assessments - the output of the
scoring formula (Rainfall severity x Susceptibility = Disruption score).
"""
from datetime import datetime
from pydantic import BaseModel


class RiskAssessmentCreate(BaseModel):
    route_segment_id: int
    disruption_score: int | None = None
    risk_badge: str | None = None
    confidence_badge: str | None = None
    calculated_at: datetime | None = None


class RiskAssessmentOut(BaseModel):
    id: int
    route_segment_id: int | None = None
    disruption_score: int | None = None
    risk_badge: str | None = None
    confidence_badge: str | None = None
    calculated_at: datetime | None = None

    model_config = {"from_attributes": True}