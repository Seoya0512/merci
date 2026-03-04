import uuid as uuid_lib

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import GroupMember, Memory, RecallLog
from app.recall.schema import RecallCreateRequest


async def _get_membership(db: AsyncSession, user_id: uuid_lib.UUID) -> GroupMember | None:
    result = await db.execute(
        select(GroupMember).where(GroupMember.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def _get_memory_in_group(
    db: AsyncSession, memory_id: uuid_lib.UUID, group_id: uuid_lib.UUID
) -> Memory:
    result = await db.execute(
        select(Memory).where(Memory.id == memory_id, Memory.group_id == group_id)
    )
    memory = result.scalar_one_or_none()
    if memory is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="추억을 찾을 수 없습니다.")
    return memory


async def create_recall(
    db: AsyncSession, memory_id: uuid_lib.UUID, body: RecallCreateRequest, current_user
) -> RecallLog:
    membership = await _get_membership(db, current_user.id)
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="그룹에 소속되어 있지 않습니다.")

    await _get_memory_in_group(db, memory_id, membership.group_id)

    log = RecallLog(
        memory_id=memory_id,
        result=body.result,
        recorded_by=current_user.id,
        visited_at=body.visited_at,
    )
    db.add(log)
    await db.flush()
    return log


async def list_recalls(
    db: AsyncSession, memory_id: uuid_lib.UUID, current_user
) -> list[RecallLog]:
    membership = await _get_membership(db, current_user.id)
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="그룹에 소속되어 있지 않습니다.")

    await _get_memory_in_group(db, memory_id, membership.group_id)

    result = await db.execute(
        select(RecallLog)
        .where(RecallLog.memory_id == memory_id)
        .order_by(RecallLog.visited_at.desc())
    )
    return list(result.scalars().all())
