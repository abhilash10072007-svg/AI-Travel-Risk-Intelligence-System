from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.route_ranking import RouteRankRequest, RankedRoute
from app.services.route_ranking import rank_routes

router = APIRouter(prefix="/api/route-ranking", tags=["route-ranking"])


@router.post(
    "",
    response_model=list[RankedRoute],
    summary="Rank alternate routes by utility",
    description="Provisional weighted formula per the concept note. Weights: safety=10, time=3, disruption=2, confidence=5.",
)
def rank(
    request: RouteRankRequest,
    current_user: User = Depends(get_current_user),
) -> list[RankedRoute]:
    return rank_routes(request.routes)