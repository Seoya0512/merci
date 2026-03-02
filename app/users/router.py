from fastapi import APIRouter, Depends, HTTPException
from app.users.schema import UserResponse, UserUpdateRequest
from app.core.dependencies import get_current_user
from app.core.responses import AUTH_RESPONSES, BAD_REQUEST
from app.models import User

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="내 정보 조회",
    description="현재 로그인한 사용자의 프로필 정보를 반환합니다.",
    responses={**AUTH_RESPONSES},
)
async def get_me(current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="내 정보 수정",
    description="현재 로그인한 사용자의 닉네임을 수정합니다.",
    responses={**AUTH_RESPONSES, **BAD_REQUEST},
)
async def update_me(
    body: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")
