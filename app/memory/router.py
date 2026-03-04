from fastapi import APIRouter, Depends, Query
from uuid import UUID
from datetime import date
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.schema import MemoryCreateRequest, MemoryUpdateRequest, MemoryResponse
from app.memory import service
from app.core.dependencies import get_current_user, get_db
from app.core.responses import AUTH_RESPONSES, BAD_REQUEST, NOT_FOUND
from app.models import User

router = APIRouter()


@router.post(
    "",
    response_model=MemoryResponse,
    status_code=201,
    summary="추억 등록",
    responses={**AUTH_RESPONSES, **BAD_REQUEST},
)
async def create_memory(
    body: MemoryCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    새 추억을 등록합니다.
    파일(사진/음성)은 서버를 경유하지 않고 Cloudflare R2에 직접 업로드한 후 해당 API를 사용합니다. 
    - 참고 API: `POST /uploads/presigned-url` → R2에 업로드할 때 사용할 `object_key` 발급
    """
    return await service.create_memory(db, body, current_user)


@router.get(
    "",
    response_model=list[MemoryResponse],
    summary="추억 목록 조회",
    responses=AUTH_RESPONSES,
)
async def list_memories(
    from_date: Optional[date] = Query(None, description="조회 시작일 (YYYY-MM-DD), year 기준 필터"),
    to_date: Optional[date] = Query(None, description="조회 종료일 (YYYY-MM-DD), year 기준 필터"),
    created_by: Optional[UUID] = Query(None, description="특정 작성자의 추억만 조회할 경우 user_id"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    현재 유저가 속한 그룹의 추억 목록을 반환합니다.

    **응답의 image_url / voice_url** 은 **1시간 유효한 presigned GET URL**입니다.
    Cloudflare R2 버킷이 private으로 설정되어 있으므로, 이 URL 없이는 파일에 접근할 수 없습니다.
    URL이 만료된 경우 이 API를 다시 호출하여 갱신된 URL을 사용하세요.
    """
    return await service.list_memories(db, current_user, from_date, to_date, created_by)


@router.get(
    "/{memory_id}",
    response_model=MemoryResponse,
    summary="추억 단건 조회",
    responses={**AUTH_RESPONSES, **NOT_FOUND},
)
async def get_memory(
    memory_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    특정 추억의 상세 정보를 반환합니다.

    상세 페이지에서는 아래 3개 API를 동시에 호출하여 화면을 구성하세요.

    - `GET /memories/{id}` — 추억 기본 정보
    - `GET /memories/{id}/recalls` — 회상 이력 및 현재 상태
    - `GET /memories/{id}/comments` — 댓글 목록

    **응답의 image_url / voice_url** 은 **1시간 유효한 presigned GET URL**입니다.
    URL이 만료된 경우 이 API를 다시 호출하여 갱신된 URL을 사용하세요.
    """
    return await service.get_memory(db, memory_id, current_user)


@router.patch(
    "/{memory_id}",
    response_model=MemoryResponse,
    summary="추억 수정",
    responses={**AUTH_RESPONSES, **BAD_REQUEST, **NOT_FOUND},
)
async def update_memory(
    memory_id: UUID,
    body: MemoryUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    추억을 부분 수정합니다. **수정할 필드만 포함하면 됩니다** (PATCH 방식).

    **파일 교체**
    - 새 파일을 교체하려면 `POST /uploads/presigned-url` 로 새 object_key 를 발급받은 뒤
      해당 값을 image_key 또는 voice_key 에 전달하세요.
    - 서버가 기존 파일을 R2에서 삭제하고 새 파일을 영구 경로로 이동합니다.

    **파일 삭제 (음성만 해당)**
    - 음성을 삭제하려면 `voice_key` 에 빈 문자열(`""`)을 전달하세요.
    - `image_key` 는 필수 항목이므로 삭제할 수 없습니다.

    **수정 권한**: 추억을 등록한 본인만 수정할 수 있습니다.
    """
    return await service.update_memory(db, memory_id, body, current_user)


@router.delete(
    "/{memory_id}",
    status_code=204,
    summary="추억 삭제",
    responses={**AUTH_RESPONSES, **NOT_FOUND},
)
async def delete_memory(
    memory_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    추억을 삭제합니다.

    DB 레코드와 함께 R2에 저장된 사진 및 음성 파일도 영구 삭제됩니다.

    **삭제 권한**: 추억을 등록한 본인만 삭제할 수 있습니다.
    """
    await service.delete_memory(db, memory_id, current_user)
