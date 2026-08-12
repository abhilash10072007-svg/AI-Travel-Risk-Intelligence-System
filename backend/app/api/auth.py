from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get the currently authenticated user",
    description="Requires a valid Firebase ID token in the Authorization header: `Bearer <token>`.",
)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user