from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from datetime import date
from typing import Optional
from app.memory.schema import MemoryCreateRequest, MemoryUpdateRequest, MemoryResponse
from app.core.dependencies import get_current_user
from app.core.responses import AUTH_RESPONSES, NOT_FOUND
from app.models import User

router = APIRouter()


@router.post(
    "",
    response_model=MemoryResponse,
    status_code=201,
    summary="추억 등록",
    description="그룹에 새 추억(사진 + 스토리)을 등록합니다.",
    responses={**AUTH_RESPONSES},
)
async def create_memory(
    body: MemoryCreateRequest,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get(
    "",
    response_model=list[MemoryResponse],
    summary="추억 목록 조회",
    description="내 그룹의 추억 목록을 조회합니다. 날짜·작성자로 필터링 가능합니다.",
    responses={**AUTH_RESPONSES},
)
async def list_memories(
    from_date: Optional[date] = Query(None, description="조회 시작일 (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="조회 종료일 (YYYY-MM-DD)"),
    created_by: Optional[UUID] = Query(None, description="작성자 user_id"),
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get(
    "/{memory_id}",
    response_model=MemoryResponse,
    summary="추억 상세 조회",
    description="특정 추억의 상세 정보를 반환합니다.",
    responses={**AUTH_RESPONSES, **NOT_FOUND},
)
async def get_memory(
    memory_id: UUID,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.patch(
    "/{memory_id}",
    response_model=MemoryResponse,
    summary="추억 수정",
    description="추억 정보를 수정합니다. 작성자(created_by)만 수정 가능합니다.",
    responses={**AUTH_RESPONSES, **NOT_FOUND},
)
async def update_memory(
    memory_id: UUID,
    body: MemoryUpdateRequest,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete(
    "/{memory_id}",
    status_code=204,
    summary="추억 삭제",
    description="추억을 삭제합니다. 작성자(created_by)만 삭제 가능합니다.",
    responses={**AUTH_RESPONSES, **NOT_FOUND},
)
async def delete_memory(
    memory_id: UUID,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")
