from fastapi import APIRouter, Depends, HTTPException
from app.group.schema import (
    GroupCreateRequest,
    GroupJoinRequest,
    GroupResponse,
    InviteCodeResponse,
)
from app.core.dependencies import get_current_user
from app.models import User

router = APIRouter()


@router.post("", response_model=GroupResponse, status_code=201)
async def create_group(
    body: GroupCreateRequest,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/join", response_model=GroupResponse)
async def join_group(
    body: GroupJoinRequest,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/me", response_model=GroupResponse)
async def get_my_group(current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/me/invite-code", response_model=InviteCodeResponse)
async def get_invite_code(current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail="Not implemented")
