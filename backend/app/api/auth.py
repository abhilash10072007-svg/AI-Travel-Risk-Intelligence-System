import random
import smtplib
import ssl
from datetime import datetime, timedelta
from email.message import EmailMessage
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])

OTP_STORE: dict[str, dict[str, Any]] = {}


def _generate_otp() -> str:
    return str(random.randint(100000, 999999))


def _otp_key(email: str) -> str:
    return email.strip().lower()


def _send_smtp_otp(email: str, otp: str) -> None:
    missing = [
        name
        for name, value in {
            "smtp_host": settings.smtp_host,
            "smtp_username": settings.smtp_username,
            "smtp_password": settings.smtp_password,
        }.items()
        if not value
    ]

    if missing:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Email delivery is not configured. Add SMTP credentials to backend/.env "
                "before enabling OTP emails."
            ),
        )

    message = EmailMessage()
    message["Subject"] = "Your travel verification code"
    message["From"] = settings.smtp_from_email or settings.smtp_username
    message["To"] = email
    message.set_content(
        "Your verification code is "
        f"{otp}. This code expires in 5 minutes."
    )

    context = ssl.create_default_context()
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls(context=context)
        server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(message)


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get the currently authenticated user",
    description="Requires a valid Firebase ID token in the Authorization header: `Bearer <token>`.",
)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post("/send-otp")
def send_otp(payload: dict[str, str]) -> dict[str, Any]:
    normalized_email = (payload.get("email") or "").strip()
    if not normalized_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required.")

    otp = _generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=5)
    OTP_STORE[_otp_key(normalized_email)] = {"otp": otp, "expires_at": expiry}

    try:
        _send_smtp_otp(normalized_email, otp)
    except HTTPException:
        OTP_STORE.pop(_otp_key(normalized_email), None)
        raise
    except Exception as exc:
        OTP_STORE.pop(_otp_key(normalized_email), None)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not send OTP email: {exc}",
        ) from exc

    return {
        "message": "OTP sent successfully.",
        "email": normalized_email,
        "sent": True,
    }


@router.post("/verify-otp")
def verify_otp(payload: dict[str, str]) -> dict[str, Any]:
    email = (payload.get("email") or "").strip()
    otp = (payload.get("otp") or "").strip()

    if not email or not otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email and OTP are required.")

    key = _otp_key(email)
    record = OTP_STORE.get(key)
    if not record:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No OTP was generated for this email.")

    if datetime.utcnow() > record["expires_at"]:
        OTP_STORE.pop(key, None)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The OTP has expired. Please request a new one.")

    is_valid = record["otp"] == otp
    if is_valid:
        OTP_STORE.pop(key, None)

    return {"verified": is_valid, "message": "OTP verified successfully." if is_valid else "Invalid OTP."}