from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime


class UserGroupInfo(BaseModel):
    id: UUID
    name: str = Field(..., description="어르신 성함 (그룹명)")
    invite_code: str = Field(..., description="가족 초대 코드")


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    provider: str
    email: str
    name: str
    nickname: str | None
    created_at: datetime
    group: UserGroupInfo | None = Field(None, description="소속 그룹 정보. 그룹이 없으면 null")
    relation: str | None = Field(None, description="그룹 내 어르신과의 관계. 미설정 시 null")


class UserUpdateRequest(BaseModel):
    nickname: str | None = None
