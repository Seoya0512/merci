from pydantic import BaseModel, ConfigDict, Field
from pydantic.aliases import AliasPath
from uuid import UUID
from datetime import datetime
from app.models import GroupRole


class GroupCreateRequest(BaseModel):
    name: str  # 어르신 성함


class GroupJoinRequest(BaseModel):
    invite_code: str


class GroupMemberRelationRequest(BaseModel):
    relation: str


class GroupMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    user_id: UUID
    name: str = Field(validation_alias=AliasPath("user", "name"))
    role: GroupRole
    relation: str | None = None
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
