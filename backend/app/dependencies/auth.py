"""
get_current_user() - FastAPI dependency. Reads the Bearer token,
verifies it against Firebase Admin Auth, and returns the matching
Supabase user row (creating it on first login).
"""
from fastapi import Depends, Header, HTTPException, status
from firebase_admin import exceptions as firebase_exceptions  # real firebase_admin.exceptions module
from sqlalchemy.orm import Session

from app.firebase.firebase_client import firebase_auth
from app.db.database import get_db
from app.models.user import User


def _extract_bearer_token(authorization: str | None) -> str:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must be in the format: Bearer <token>",
        )

    return parts[1]


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    token = _extract_bearer_token(authorization)

    try:
        decoded_token = firebase_auth.verify_id_token(token)
    except firebase_auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase token has expired",
        )
    except firebase_auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase token is invalid",
        )
    except firebase_exceptions.FirebaseError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not verify Firebase token",
        )

    firebase_uid = decoded_token["uid"]
    email = decoded_token.get("email")
    name = decoded_token.get("name")

    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if user is None:
        user = User(firebase_uid=firebase_uid, email=email, name=name)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user