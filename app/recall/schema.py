from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from app.models import RecallResult


class RecallCreateRequest(BaseModel):
    result: RecallResult
    visited_at: datetime


class RecallResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    memory_id: UUID
    result: RecallResult
    recorded_by: UUID
    visited_at: datetime
