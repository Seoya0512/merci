from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime, date


class MemoryCreateRequest(BaseModel):
    image_url: str
    year: int
    location: str
    people: str
    story: str
    voice_url: str | None = None


class MemoryUpdateRequest(BaseModel):
    image_url: str | None = None
    year: int | None = None
    location: str | None = None
    people: str | None = None
    story: str | None = None
    voice_url: str | None = None


class MemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    group_id: UUID
    image_url: str
    year: int
    location: str
    people: str
    story: str
    voice_url: str | None
    created_by: UUID
    created_at: datetime
    has_badge: bool = False  # 기억하심 recall_log 존재 여부
