"""
Request/response shapes for alternate-route utility ranking (PDF Section 3.3).
"""
from pydantic import BaseModel, Field


class RouteOption(BaseModel):
    """One candidate route to compare against others."""
    name: str
    avg_risk_score: float = Field(gt=0, description="Mean disruption/risk score across zones")
    added_time_hours: float = Field(ge=0, description="Extra travel time vs baseline route")
    disrupted_zone_count: int = Field(ge=0, description="Number of zones with elevated disruption")
    confidence_score: float = Field(ge=0, le=1, description="Model confidence in the assessment (0-1)")


class RouteRankRequest(BaseModel):
    """Batch of routes to rank by utility."""
    routes: list[RouteOption] = Field(min_length=1)


class RankedRoute(BaseModel):
    """Route option with computed utility, sorted highest-first by the service."""
    name: str
    utility: float
    avg_risk_score: float
    added_time_hours: float
    disrupted_zone_count: int
    confidence_score: float
