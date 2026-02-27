from fastapi import APIRouter, Depends, HTTPException
from app.users.schema import UserResponse, UserUpdateRequest
from app.core.dependencies import get_current_user
from app.models import User

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.patch("/me", response_model=UserResponse)
async def update_me(
    body: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")
