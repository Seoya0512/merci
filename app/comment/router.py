from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.comment.schema import CommentCreateRequest, CommentUpdateRequest, CommentResponse
from app.comment import service
from app.core.dependencies import get_current_user, get_db
from app.core.responses import AUTH_RESPONSES, NOT_FOUND
from app.models import User

router = APIRouter()


@router.get(
    "/{memory_id}/comments",
    response_model=list[CommentResponse],
    summary="댓글 목록 조회",
    responses={**AUTH_RESPONSES, **NOT_FOUND},
)
async def get_comments(
    memory_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    특정 추억의 댓글 목록을 반환합니다.

    같은 그룹 멤버만 조회할 수 있습니다.
    """
    return await service.list_comments(db, memory_id, current_user)


@router.post(
    "/{memory_id}/comments",
    response_model=CommentResponse,
    status_code=201,
    summary="댓글 등록",
    responses={**AUTH_RESPONSES, **NOT_FOUND},
)
async def create_comment(
    memory_id: UUID,
    body: CommentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    특정 추억에 댓글을 등록합니다.

    같은 그룹 멤버만 댓글을 작성할 수 있습니다.
    """
    return await service.create_comment(db, memory_id, body, current_user)


@router.patch(
    "/{memory_id}/comments/{comment_id}",
    response_model=CommentResponse,
    summary="댓글 수정",
    responses={**AUTH_RESPONSES, **NOT_FOUND},
)
async def update_comment(
    memory_id: UUID,
    comment_id: UUID,
    body: CommentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    댓글 내용을 수정합니다.

    본인이 작성한 댓글만 수정할 수 있습니다.
    """
    return await service.update_comment(db, memory_id, comment_id, body, current_user)


@router.delete(
    "/{memory_id}/comments/{comment_id}",
    status_code=204,
    summary="댓글 삭제",
    responses={**AUTH_RESPONSES, **NOT_FOUND},
)
async def delete_comment(
    memory_id: UUID,
    comment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    댓글을 삭제합니다.

    본인이 작성한 댓글만 삭제할 수 있습니다.
    """
    await service.delete_comment(db, memory_id, comment_id, current_user)
