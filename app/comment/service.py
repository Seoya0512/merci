from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.comment.schema import CommentCreateRequest, CommentUpdateRequest, CommentResponse
from app.core.utils import get_membership_or_403
from app.models import Comment, Memory, User, GroupMember


async def _get_memory_in_group(db: AsyncSession, memory_id: UUID, group_id: UUID) -> Memory:
    result = await db.execute(
        select(Memory).where(Memory.id == memory_id, Memory.group_id == group_id)
    )
    memory = result.scalar_one_or_none()
    if memory is None:
        raise HTTPException(status_code=404, detail="추억을 찾을 수 없습니다.")
    return memory


def _to_response(comment: Comment, group_id: UUID) -> CommentResponse:
    relation = next(
        (m.relation for m in comment.user.group_memberships if m.group_id == group_id),
        None,
    ) if comment.user else None
    return CommentResponse(
        id=comment.id,
        memory_id=comment.memory_id,
        user_id=comment.user_id,
        content=comment.content,
        created_at=comment.created_at,
        author_name=comment.user.name if comment.user else None,
        relation=relation,
    )


async def list_comments(db: AsyncSession, memory_id: UUID, current_user: User) -> list[CommentResponse]:
    membership = await get_membership_or_403(db, current_user.id)
    await _get_memory_in_group(db, memory_id, membership.group_id)

    result = await db.execute(
        select(Comment)
        .where(Comment.memory_id == memory_id)
        .options(selectinload(Comment.user).selectinload(User.group_memberships))
        .order_by(Comment.created_at.asc())
    )
    comments = result.scalars().all()
    return [_to_response(c, membership.group_id) for c in comments]


async def create_comment(
    db: AsyncSession, memory_id: UUID, body: CommentCreateRequest, current_user: User
) -> CommentResponse:
    membership = await get_membership_or_403(db, current_user.id)
    await _get_memory_in_group(db, memory_id, membership.group_id)

    comment = Comment(
        memory_id=memory_id,
        user_id=current_user.id,
        content=body.content,
    )
    db.add(comment)
    await db.flush()

    await db.refresh(comment, ["user"])
    await db.refresh(comment.user, ["group_memberships"])
    return _to_response(comment, membership.group_id)


async def update_comment(
    db: AsyncSession, memory_id: UUID, comment_id: UUID, body: CommentUpdateRequest, current_user: User
) -> CommentResponse:
    membership = await get_membership_or_403(db, current_user.id)
    await _get_memory_in_group(db, memory_id, membership.group_id)

    result = await db.execute(
        select(Comment)
        .where(Comment.id == comment_id, Comment.memory_id == memory_id)
        .options(selectinload(Comment.user).selectinload(User.group_memberships))
    )
    comment = result.scalar_one_or_none()
    if comment is None:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인이 작성한 댓글만 수정할 수 있습니다.")

    comment.content = body.content
    db.add(comment)
    return _to_response(comment, membership.group_id)


async def delete_comment(
    db: AsyncSession, memory_id: UUID, comment_id: UUID, current_user: User
) -> None:
    membership = await get_membership_or_403(db, current_user.id)
    await _get_memory_in_group(db, memory_id, membership.group_id)

    result = await db.execute(
        select(Comment).where(Comment.id == comment_id, Comment.memory_id == memory_id)
    )
    comment = result.scalar_one_or_none()
    if comment is None:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인이 작성한 댓글만 삭제할 수 있습니다.")

    await db.delete(comment)
