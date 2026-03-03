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
from app.models import User

router = APIRouter()


@router.post("", response_model=InviteCodeResponse, status_code=201)
async def create_group_endpoint(
    body: GroupCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    그룹을 생성합니다.
    1. 이미 그룹에 소속된 경우 409 반환
    2. 그룹 생성 및 초대 코드 발급
    3. 생성자를 OWNER로 그룹에 등록
    4. 초대 코드 반환
    """
    invite_code = await create_group(db, current_user, body)
    return InviteCodeResponse(invite_code=invite_code)


@router.post("/join", response_model=GroupResponse)
async def join_group_endpoint(
    body: GroupJoinRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    초대 코드로 그룹에 참여합니다.
    1. 이미 그룹에 소속된 경우 409 반환
    2. 초대 코드로 그룹 조회 (없으면 404)
    3. 현재 유저를 MEMBER로 그룹에 등록
    4. 그룹 정보 및 멤버 목록 반환
    """
    return await join_group(db, current_user, body)


@router.get("/me", response_model=GroupResponse)
async def get_my_group_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    내가 소속된 그룹 정보를 조회합니다.
    1. 소속 그룹이 없으면 404 반환
    2. 그룹 정보 및 멤버 목록 반환
    """
    return await get_my_group(db, current_user)


@router.get("/me/invite-code", response_model=InviteCodeResponse)
async def get_invite_code_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    내 그룹의 초대 코드를 조회합니다.
    1. 소속 그룹이 없으면 404 반환
    2. 초대 코드 반환
    """
    invite_code = await get_invite_code(db, current_user)
    return InviteCodeResponse(invite_code=invite_code)


@router.patch("/me/relation", response_model=GroupResponse)
async def update_relation_endpoint(
    body: GroupMemberRelationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    그룹 내 나의 어르신과의 관계를 수정합니다. (예: 아들, 딸, 간병인)
    1. 소속 그룹이 없으면 404 반환
    2. 관계 정보 업데이트
    3. 그룹 정보 및 멤버 목록 반환
    """
    return await update_relation(db, current_user, body.relation)
