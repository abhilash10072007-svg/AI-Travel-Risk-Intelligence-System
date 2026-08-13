"""
Alternate-route utility ranking, per PDF Section 3.3:
U(route) = 10 x (1/avg_risk_score) + 3 x (1/(1+added_time_hours))
           + 2 x (1/(1+disrupted_zone_count)) + 5 x confidence_score
Weights are stated explicitly, not hidden - matches the PDF's "no black box" claim.
"""
from app.schemas.route_ranking import RouteOption, RankedRoute


def compute_utility(route: RouteOption) -> float:
    safety_term = 10 * (1 / route.avg_risk_score) if route.avg_risk_score > 0 else 10
    time_term = 3 * (1 / (1 + route.added_time_hours))
    disruption_term = 2 * (1 / (1 + route.disrupted_zone_count))
    confidence_term = 5 * route.confidence_score
    return round(safety_term + time_term + disruption_term + confidence_term, 3)


def rank_routes(routes: list[RouteOption]) -> list[RankedRoute]:
    ranked = [
        RankedRoute(
            name=r.name,
            utility=compute_utility(r),
            avg_risk_score=r.avg_risk_score,
            added_time_hours=r.added_time_hours,
            disrupted_zone_count=r.disrupted_zone_count,
            confidence_score=r.confidence_score,
        )
        for r in routes
    ]
    return sorted(ranked, key=lambda r: r.utility, reverse=True)