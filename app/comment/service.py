from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.comment.schema import CommentCreateRequest, CommentUpdateRequest, CommentResponse
from app.models import Comment, GroupMember, Memory, User


async def _get_group_id(db: AsyncSession, user: User) -> UUID:
    result = await db.execute(
        select(GroupMember.group_id).where(GroupMember.user_id == user.id)
    )
    group_id = result.scalar_one_or_none()
    if group_id is None:
        raise HTTPException(status_code=403, detail="그룹에 속해 있지 않습니다.")
    return group_id


async def _get_memory(db: AsyncSession, memory_id: UUID, group_id: UUID) -> Memory:
    result = await db.execute(
        select(Memory).where(Memory.id == memory_id, Memory.group_id == group_id)
    )
    memory = result.scalar_one_or_none()
    if memory is None:
        raise HTTPException(status_code=404, detail="추억을 찾을 수 없습니다.")
    return memory


def _to_response(comment: Comment) -> CommentResponse:
    return CommentResponse(
        id=comment.id,
        memory_id=comment.memory_id,
        user_id=comment.user_id,
        content=comment.content,
        created_at=comment.created_at,
        author_name=comment.user.name if comment.user else None,
    )


async def list_comments(db: AsyncSession, memory_id: UUID, current_user: User) -> list[CommentResponse]:
    group_id = await _get_group_id(db, current_user)
    await _get_memory(db, memory_id, group_id)

    result = await db.execute(
        select(Comment)
        .where(Comment.memory_id == memory_id)
        .options(selectinload(Comment.user))
        .order_by(Comment.created_at.asc())
    )
    comments = result.scalars().all()
    return [_to_response(c) for c in comments]


async def create_comment(
    db: AsyncSession, memory_id: UUID, body: CommentCreateRequest, current_user: User
) -> CommentResponse:
    group_id = await _get_group_id(db, current_user)
    await _get_memory(db, memory_id, group_id)

    comment = Comment(
        memory_id=memory_id,
        user_id=current_user.id,
        content=body.content,
    )
    db.add(comment)
    await db.flush()

    await db.refresh(comment, ["user"])
    return _to_response(comment)


async def update_comment(
    db: AsyncSession, memory_id: UUID, comment_id: UUID, body: CommentUpdateRequest, current_user: User
) -> CommentResponse:
    group_id = await _get_group_id(db, current_user)
    await _get_memory(db, memory_id, group_id)

    result = await db.execute(
        select(Comment)
        .where(Comment.id == comment_id, Comment.memory_id == memory_id)
        .options(selectinload(Comment.user))
    )
    comment = result.scalar_one_or_none()
    if comment is None:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인이 작성한 댓글만 수정할 수 있습니다.")

    comment.content = body.content
    db.add(comment)
    return _to_response(comment)


async def delete_comment(
    db: AsyncSession, memory_id: UUID, comment_id: UUID, current_user: User
) -> None:
    group_id = await _get_group_id(db, current_user)
    await _get_memory(db, memory_id, group_id)

    result = await db.execute(
        select(Comment).where(Comment.id == comment_id, Comment.memory_id == memory_id)
    )
    comment = result.scalar_one_or_none()
    if comment is None:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인이 작성한 댓글만 삭제할 수 있습니다.")

    await db.delete(comment)
