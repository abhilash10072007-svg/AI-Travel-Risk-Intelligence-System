"""
FastAPI application entrypoint.

Phase 1: app setup, CORS, error handling, /api/auth/me.
Phase 2: Trip Input API (/api/trips).
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api import auth
from app.api import trips
from app.api import route_segments
from app.api import risk_assessments
from app.api import alerts
from app.api import route_ranking
from app.api import riskApi

app = FastAPI(
    title="AI Travel Risk Intelligence System - Backend",
    description="FastAPI foundation + Firebase authentication + Supabase Postgres + Trip Input API + Risk Engine.",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(trips.router)
app.include_router(route_segments.router)
app.include_router(risk_assessments.router)
app.include_router(alerts.router)
app.include_router(route_ranking.router)
app.include_router(riskApi.router)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "environment": settings.environment}