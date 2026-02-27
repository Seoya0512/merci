from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class CommentCreateRequest(BaseModel):
    content: str


class CommentUpdateRequest(BaseModel):
    content: str


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    memory_id: UUID
    user_id: UUID
    content: str
    created_at: datetime
    author_nickname: str | None = None
