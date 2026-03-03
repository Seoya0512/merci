import uuid as uuid_lib
import secrets
import string

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Group, GroupMember, GroupRole, User
from app.group.schema import GroupCreateRequest, GroupJoinRequest


def _generate_invite_code() -> str:
    chars = string.ascii_uppercase + string.digits
    part1 = "".join(secrets.choice(chars) for _ in range(4))
    part2 = "".join(secrets.choice(chars) for _ in range(2))
    return f"MC-{part1}-{part2}"


async def _get_group_with_members(db: AsyncSession, group_id: uuid_lib.UUID) -> Group:
    result = await db.execute(
        select(Group)
        .where(Group.id == group_id)
        .options(selectinload(Group.members).selectinload(GroupMember.user))
    )
    return result.scalar_one()


async def _get_membership(db: AsyncSession, user_id: uuid_lib.UUID) -> GroupMember | None:
    result = await db.execute(
        select(GroupMember).where(GroupMember.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_group(db: AsyncSession, user: User, body: GroupCreateRequest) -> Group:
    if await _get_membership(db, user.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 그룹에 소속되어 있습니다.",
        )

    group_id = uuid_lib.uuid4()
    invite_code = _generate_invite_code()
    group = Group(id=group_id, name=body.name, invite_code=invite_code, created_by=user.id)
    member = GroupMember(group_id=group_id, user_id=user.id, role=GroupRole.OWNER)
    db.add(group)
    db.add(member)

    return invite_code


async def join_group(db: AsyncSession, user: User, body: GroupJoinRequest) -> Group:
    if await _get_membership(db, user.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 그룹에 소속되어 있습니다.",
        )

    result = await db.execute(select(Group).where(Group.invite_code == body.invite_code))
    group = result.scalar_one_or_none()
    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="초대 코드가 유효하지 않습니다.",
        )

    member = GroupMember(group_id=group.id, user_id=user.id, role=GroupRole.MEMBER)
    db.add(member)
    await db.flush()

    return await _get_group_with_members(db, group.id)


async def get_my_group(db: AsyncSession, user: User) -> Group:
    membership = await _get_membership(db, user.id)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="소속된 그룹이 없습니다.",
        )

    return await _get_group_with_members(db, membership.group_id)


async def get_invite_code(db: AsyncSession, user: User) -> str:
    membership = await _get_membership(db, user.id)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="소속된 그룹이 없습니다.",
        )

    result = await db.execute(select(Group).where(Group.id == membership.group_id))
    group = result.scalar_one()
    return group.invite_code


async def update_relation(db: AsyncSession, user: User, relation: str) -> Group:
    membership = await _get_membership(db, user.id)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="소속된 그룹이 없습니다.",
        )

    membership.relation = relation
    db.add(membership)
    await db.flush()

    return await _get_group_with_members(db, membership.group_id)
