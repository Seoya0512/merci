import uuid as uuid_lib
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import get_membership_or_403
from app.models import Memory, RecallLog
from app.recall.schema import RecallCreateRequest


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
    membership = await get_membership_or_403(db, current_user.id)
    await _get_memory_in_group(db, memory_id, membership.group_id)

    log = RecallLog(
        memory_id=memory_id,
        result=body.result,
        recorded_by=current_user.id,
        visited_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db.add(log)
    await db.flush()
    return log


async def list_recalls(
    db: AsyncSession, memory_id: uuid_lib.UUID, current_user
) -> list[RecallLog]:
    membership = await get_membership_or_403(db, current_user.id)
    await _get_memory_in_group(db, memory_id, membership.group_id)

    result = await db.execute(
        select(RecallLog)
        .where(RecallLog.memory_id == memory_id)
        .order_by(RecallLog.visited_at.desc())
    )
    return list(result.scalars().all())
