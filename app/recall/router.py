from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.recall.schema import RecallCreateRequest, RecallResponse
from app.recall import service
from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.models import User

router = APIRouter()


@router.post(
    "/{memory_id}/recalls",
    response_model=RecallResponse,
    status_code=201,
    summary="회상 결과 기록",
)
async def create_recall(
    memory_id: UUID,
    body: RecallCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    특정 추억에 대한 어르신의 회상 결과를 기록합니다.

    **결과값 (`result`)**

    - `기억하심`: 어르신이 추억을 기억하신 경우
    - `가물가물`: 희미하게 기억하시는 경우
    - `낯설어하심`: 기억하지 못하시는 경우
    """
    log = await service.create_recall(db, memory_id, body, current_user)
    return log


@router.get(
    "/{memory_id}/recalls",
    response_model=list[RecallResponse],
    summary="회상 이력 조회",
)
async def list_recalls(
    memory_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    특정 추억의 회상 기록 이력을 최신순으로 반환합니다.

    **목록의 첫 번째 항목이 현재 상태**입니다.
    """
    logs = await service.list_recalls(db, memory_id, current_user)
    return logs
