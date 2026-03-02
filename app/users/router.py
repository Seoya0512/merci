from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.schema import UserResponse, UserUpdateRequest
from app.users.service import update_user
from app.core.dependencies import get_current_user, get_db
from app.models import User

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    body: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await update_user(db, current_user, body)
