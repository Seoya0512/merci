from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from app.recall.schema import RecallCreateRequest, RecallResponse
from app.core.dependencies import get_current_user
from app.models import User

router = APIRouter()


@router.post("/{memory_id}/recalls", response_model=RecallResponse, status_code=201)
async def create_recall(
    memory_id: UUID,
    body: RecallCreateRequest,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")
