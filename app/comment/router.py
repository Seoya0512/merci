from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from app.comment.schema import CommentCreateRequest, CommentUpdateRequest, CommentResponse
from app.core.dependencies import get_current_user
from app.models import User

router = APIRouter()


@router.get("/{memory_id}/comments", response_model=list[CommentResponse])
async def get_comments(
    memory_id: UUID,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/{memory_id}/comments", response_model=CommentResponse, status_code=201)
async def create_comment(
    memory_id: UUID,
    body: CommentCreateRequest,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.patch("/{memory_id}/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    memory_id: UUID,
    comment_id: UUID,
    body: CommentUpdateRequest,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/{memory_id}/comments/{comment_id}", status_code=204)
async def delete_comment(
    memory_id: UUID,
    comment_id: UUID,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")
