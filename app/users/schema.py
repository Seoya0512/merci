from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    provider: str
    email: str
    name: str
    nickname: str | None
    created_at: datetime


class UserUpdateRequest(BaseModel):
    nickname: str | None = None
