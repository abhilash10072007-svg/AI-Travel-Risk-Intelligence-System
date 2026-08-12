# → Abhilash (app setup, wiring everything)

"""
FastAPI application entrypoint. Phase 1 scope: app setup, CORS,
error handling, and the /api/auth/me route against the existing
Supabase `users` table.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api import auth

app = FastAPI(
    title="AI Travel Risk Intelligence System - Backend",
    description="Phase 1: FastAPI foundation + Firebase authentication + Supabase Postgres.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "environment": settings.environment}