from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Group, GroupMember, User
from app.users.schema import UserResponse, UserGroupInfo, UserUpdateRequest


async def get_me(db: AsyncSession, user: User) -> UserResponse:
    result = await db.execute(
        select(GroupMember)
        .where(GroupMember.user_id == user.id)
        .options(selectinload(GroupMember.group))
    )
    membership = result.scalar_one_or_none()

    group_info = None
    relation = None
    if membership:
        group_info = UserGroupInfo(
            id=membership.group.id,
            name=membership.group.name,
            invite_code=membership.group.invite_code,
        )
        relation = membership.relation

    return UserResponse(
        id=user.id,
        provider=user.provider,
        email=user.email,
        name=user.name,
        nickname=user.nickname,
        created_at=user.created_at,
        group=group_info,
        relation=relation,
    )


async def update_user(db: AsyncSession, user: User, body: UserUpdateRequest) -> User:
    if body.nickname is not None:
        user.nickname = body.nickname
    db.add(user)
    return user
