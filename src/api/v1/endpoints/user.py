from fastapi import APIRouter, Depends
from models.user import User

from api.v1.dependencies.auth import current_active_user

router = APIRouter()


@router.get("/me")
async def current_user(user: User = Depends(current_active_user)) -> User:
    return user
