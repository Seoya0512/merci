from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from app.models import RecallResult


class RecallCreateRequest(BaseModel):
    result: RecallResult = Field(..., description="`기억하심` / `가물가물` / `낯설어하심` 중 하나")


class RecallResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    memory_id: UUID
    result: RecallResult = Field(..., description="회상 결과: `기억하심` / `가물가물` / `낯설어하심`")
    recorded_by: UUID = Field(..., description="기록한 가족 구성원의 user_id")
    visited_at: datetime = Field(..., description="어르신과 함께 추억을 본 날짜")
