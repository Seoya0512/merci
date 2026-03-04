from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.group.schema import (
    GroupCreateRequest,
    GroupJoinRequest,
    GroupMemberRelationRequest,
    GroupResponse,
    InviteCodeResponse,
)
from app.group.service import (
    create_group,
    join_group,
    get_my_group,
    get_invite_code,
    update_relation,
)
from app.core.dependencies import get_current_user, get_db
from app.core.responses import AUTH_RESPONSES, NOT_FOUND, CONFLICT
from app.models import User

router = APIRouter()


@router.post(
    "",
    response_model=InviteCodeResponse,
    status_code=201,
    summary="그룹 생성",
    responses={**AUTH_RESPONSES, **CONFLICT},
)
async def create_group_endpoint(
    body: GroupCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    새 그룹을 생성합니다.

    - 이미 다른 그룹에 소속된 경우 409를 반환합니다. (MVP: 1인 1그룹)
    - 생성자는 자동으로 `OWNER` 역할로 등록됩니다.
    - 생성 시 초대 코드가 자동 발급됩니다. 초대 코드는 `GET /groups/me/invite-code` 로 다시 조회할 수 있습니다.
    """
    invite_code = await create_group(db, current_user, body)
    return InviteCodeResponse(invite_code=invite_code)


@router.post(
    "/join",
    response_model=GroupResponse,
    summary="초대 코드로 그룹 참여",
    responses={**AUTH_RESPONSES, **NOT_FOUND, **CONFLICT},
)
async def join_group_endpoint(
    body: GroupJoinRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    초대 코드로 기존 그룹에 참여합니다.

    - 이미 다른 그룹에 소속된 경우 409를 반환합니다. (MVP: 1인 1그룹)
    - 유효하지 않은 초대 코드는 404를 반환합니다.
    - 참여 후 `MEMBER` 역할로 등록됩니다.
    """
    return await join_group(db, current_user, body)


@router.get(
    "/me",
    response_model=GroupResponse,
    summary="내 그룹 조회",
    responses={**AUTH_RESPONSES, **NOT_FOUND},
)
async def get_my_group_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    현재 유저가 소속된 그룹 정보와 멤버 목록을 반환합니다.

    소속된 그룹이 없으면 404를 반환합니다.
    """
    return await get_my_group(db, current_user)


@router.get(
    "/me/invite-code",
    response_model=InviteCodeResponse,
    summary="내 그룹 초대 코드 조회",
    responses={**AUTH_RESPONSES, **NOT_FOUND},
)
async def get_invite_code_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    내 그룹의 초대 코드를 조회합니다.

    초대 코드를 다른 가족에게 공유하면 `POST /groups/join` 으로 그룹에 참여할 수 있습니다.
    소속된 그룹이 없으면 404를 반환합니다.
    """
    invite_code = await get_invite_code(db, current_user)
    return InviteCodeResponse(invite_code=invite_code)


@router.patch(
    "/me/relation",
    response_model=GroupResponse,
    summary="어르신과의 관계 수정",
    responses={**AUTH_RESPONSES, **NOT_FOUND},
)
async def update_relation_endpoint(
    body: GroupMemberRelationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    그룹 내 나의 어르신과의 관계를 수정합니다.

    예: `아들`, `딸`, `며느리`, `간병인` 등 자유 입력입니다.
    소속된 그룹이 없으면 404를 반환합니다.
    """
    return await update_relation(db, current_user, body.relation)
