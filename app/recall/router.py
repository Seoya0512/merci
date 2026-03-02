from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from app.recall.schema import RecallCreateRequest, RecallResponse
from app.core.dependencies import get_current_user
from app.core.responses import AUTH_RESPONSES, NOT_FOUND
from app.models import User

router = APIRouter()


@router.post(
    "/{memory_id}/recalls",
    response_model=RecallResponse,
    status_code=201,
    summary="회상 결과 기록",
    description="추억을 보여줬을 때 어르신의 회상 결과(기억하심/가물가물/낯설어하심)를 기록합니다.",
    responses={**AUTH_RESPONSES, **NOT_FOUND},
)
async def create_recall(
    memory_id: UUID,
    body: RecallCreateRequest,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")
