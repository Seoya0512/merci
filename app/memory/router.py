from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from datetime import date
from typing import Optional
from app.memory.schema import MemoryCreateRequest, MemoryUpdateRequest, MemoryResponse
from app.core.dependencies import get_current_user
from app.models import User

router = APIRouter()


@router.post("", response_model=MemoryResponse, status_code=201)
async def create_memory(
    body: MemoryCreateRequest,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("", response_model=list[MemoryResponse])
async def list_memories(
    from_date: Optional[date] = Query(None, description="조회 시작일 (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="조회 종료일 (YYYY-MM-DD)"),
    created_by: Optional[UUID] = Query(None, description="작성자 user_id"),
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: UUID,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.patch("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: UUID,
    body: MemoryUpdateRequest,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/{memory_id}", status_code=204)
async def delete_memory(
    memory_id: UUID,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")
