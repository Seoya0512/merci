from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from app.models import GroupRole


class GroupCreateRequest(BaseModel):
    name: str  # 어르신 성함


class GroupJoinRequest(BaseModel):
    invite_code: str


class GroupMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    nickname: str | None
    role: GroupRole
    joined_at: datetime


class GroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    invite_code: str
    created_by: UUID
    created_at: datetime
    members: list[GroupMemberResponse] = []


class InviteCodeResponse(BaseModel):
    invite_code: str
