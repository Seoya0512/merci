from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import GroupMember


async def get_membership_or_403(db: AsyncSession, user_id: UUID) -> GroupMember:
    result = await db.execute(
        select(GroupMember).where(GroupMember.user_id == user_id)
    )
    membership = result.scalar_one_or_none()
    if membership is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="그룹에 소속되어 있지 않습니다.")
    return membership
