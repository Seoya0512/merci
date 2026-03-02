from fastapi import APIRouter, Depends, HTTPException
from app.group.schema import (
    GroupCreateRequest,
    GroupJoinRequest,
    GroupResponse,
    InviteCodeResponse,
)
from app.core.dependencies import get_current_user
from app.core.responses import AUTH_RESPONSES, BAD_REQUEST, NOT_FOUND, CONFLICT
from app.models import User

router = APIRouter()


@router.post(
    "",
    response_model=GroupResponse,
    status_code=201,
    summary="그룹 생성",
    description="새 그룹을 생성합니다. MVP에서 유저당 1개 그룹만 소속 가능합니다.",
    responses={**AUTH_RESPONSES, **CONFLICT},
)
async def create_group(
    body: GroupCreateRequest,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post(
    "/join",
    response_model=GroupResponse,
    summary="그룹 참여",
    description="초대 코드로 그룹에 참여합니다.",
    responses={**AUTH_RESPONSES, **BAD_REQUEST, **CONFLICT},
)
async def join_group(
    body: GroupJoinRequest,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get(
    "/me",
    response_model=GroupResponse,
    summary="내 그룹 조회",
    description="현재 로그인한 사용자가 속한 그룹 정보를 반환합니다.",
    responses={**AUTH_RESPONSES, **NOT_FOUND},
)
async def get_my_group(current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get(
    "/me/invite-code",
    response_model=InviteCodeResponse,
    summary="초대 코드 조회",
    description="내 그룹의 초대 코드를 반환합니다. 그룹 멤버 전체 접근 가능합니다.",
    responses={**AUTH_RESPONSES, **NOT_FOUND},
)
async def get_invite_code(current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail="Not implemented")
