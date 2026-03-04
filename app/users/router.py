from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.schema import UserResponse, UserUpdateRequest
from app.users import service
from app.core.dependencies import get_current_user, get_db
from app.core.responses import AUTH_RESPONSES
from app.models import User

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="내 프로필 조회",
    responses=AUTH_RESPONSES,
)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    현재 로그인한 유저의 프로필 정보를 반환합니다.

    소속 그룹이 있으면 `group` (그룹명, 초대 코드)과 `relation` (어르신과의 관계)을 함께 반환합니다.

    그룹에 소속되지 않은 경우 `group` 과 `relation` 은 `null` 입니다.
    """
    return await service.get_me(db, current_user)


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="내 닉네임 수정",
    responses=AUTH_RESPONSES,
)
async def update_me(
    body: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    현재 로그인한 유저의 닉네임을 수정합니다.
    """
    updated = await service.update_user(db, current_user, body)
    return await service.get_me(db, updated)
