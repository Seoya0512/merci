from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from app.comment.schema import CommentCreateRequest, CommentUpdateRequest, CommentResponse
from app.core.dependencies import get_current_user
from app.core.responses import AUTH_RESPONSES, NOT_FOUND
from app.models import User

router = APIRouter()


@router.get(
    "/{memory_id}/comments",
    response_model=list[CommentResponse],
    summary="댓글 목록 조회",
    description="특정 추억의 댓글 목록을 반환합니다.",
    responses={**AUTH_RESPONSES, **NOT_FOUND},
)
async def get_comments(
    memory_id: UUID,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post(
    "/{memory_id}/comments",
    response_model=CommentResponse,
    status_code=201,
    summary="댓글 작성",
    description="특정 추억에 댓글을 작성합니다.",
    responses={**AUTH_RESPONSES, **NOT_FOUND},
)
async def create_comment(
    memory_id: UUID,
    body: CommentCreateRequest,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.patch(
    "/{memory_id}/comments/{comment_id}",
    response_model=CommentResponse,
    summary="댓글 수정",
    description="댓글을 수정합니다. 작성자(user_id)만 수정 가능합니다.",
    responses={**AUTH_RESPONSES, **NOT_FOUND},
)
async def update_comment(
    memory_id: UUID,
    comment_id: UUID,
    body: CommentUpdateRequest,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete(
    "/{memory_id}/comments/{comment_id}",
    status_code=204,
    summary="댓글 삭제",
    description="댓글을 삭제합니다. 작성자(user_id)만 삭제 가능합니다.",
    responses={**AUTH_RESPONSES, **NOT_FOUND},
)
async def delete_comment(
    memory_id: UUID,
    comment_id: UUID,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")
