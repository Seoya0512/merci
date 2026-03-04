import uuid as uuid_lib
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.storage import move_object, delete_object, public_url, object_key_from_url, generate_presigned_get_url
from app.models import GroupMember, Memory, RecallResult
from app.memory.schema import MemoryCreateRequest, MemoryUpdateRequest


async def _get_membership(db: AsyncSession, user_id: uuid_lib.UUID) -> GroupMember | None:
    result = await db.execute(
        select(GroupMember).where(GroupMember.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def _get_memory_or_404(db: AsyncSession, memory_id: uuid_lib.UUID) -> Memory:
    result = await db.execute(
        select(Memory)
        .where(Memory.id == memory_id)
        .options(selectinload(Memory.recall_logs))
    )
    memory = result.scalar_one_or_none()
    if memory is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="추억을 찾을 수 없습니다.")
    return memory


def _has_badge(memory: Memory) -> bool:
    """가장 최근 회상 결과가 '기억하심'인 경우에만 True."""
    if not memory.recall_logs:
        return False
    most_recent = max(memory.recall_logs, key=lambda log: log.visited_at)
    return most_recent.result == RecallResult.REMEMBERED


def _to_signed(memory: Memory) -> dict:
    """DB에 저장된 URL을 presigned GET URL로 변환한 응답 dict를 반환한다."""
    return {
        "id": memory.id,
        "group_id": memory.group_id,
        "title": memory.title,
        "image_url": generate_presigned_get_url(object_key_from_url(memory.image_url)),
        "year": memory.year,
        "location": memory.location,
        "people": memory.people,
        "story": memory.story,
        "voice_url": (
            generate_presigned_get_url(object_key_from_url(memory.voice_url))
            if memory.voice_url else None
        ),
        "created_by": memory.created_by,
        "created_at": memory.created_at,
    }


def _validate_temp_key(key: str, prefix: str) -> None:
    if not key.startswith(f"temp/{prefix}/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"유효하지 않은 object_key입니다. 'temp/{prefix}/'로 시작해야 합니다.",
        )


async def _move_to_permanent(temp_key: str, category: str, group_id: uuid_lib.UUID) -> str:
    filename = temp_key.split("/")[-1]
    permanent_key = f"{category}/{group_id}/{filename}"
    await move_object(temp_key, permanent_key)
    return public_url(permanent_key)


async def create_memory(
    db: AsyncSession, body: MemoryCreateRequest, current_user
) -> Memory:
    membership = await _get_membership(db, current_user.id)
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="그룹에 소속되어 있지 않습니다.")

    _validate_temp_key(body.image_key, "images")
    if body.voice_key:
        _validate_temp_key(body.voice_key, "voices")

    image_url = await _move_to_permanent(body.image_key, "images", membership.group_id)
    voice_url = None
    if body.voice_key:
        voice_url = await _move_to_permanent(body.voice_key, "voices", membership.group_id)

    memory = Memory(
        group_id=membership.group_id,
        title=body.title,
        image_url=image_url,
        year=body.year,
        location=body.location,
        people=body.people,
        story=body.story,
        voice_url=voice_url,
        created_by=current_user.id,
    )
    db.add(memory)
    await db.flush()

    result = await db.execute(
        select(Memory)
        .where(Memory.id == memory.id)
        .options(selectinload(Memory.recall_logs))
    )
    saved = result.scalar_one()
    return {"memory": _to_signed(saved), "has_badge": False}


async def list_memories(
    db: AsyncSession,
    current_user,
    from_date: date | None = None,
    to_date: date | None = None,
    created_by: uuid_lib.UUID | None = None,
) -> list[dict]:
    membership = await _get_membership(db, current_user.id)
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="그룹에 소속되어 있지 않습니다.")

    conditions = [Memory.group_id == membership.group_id]
    if from_date:
        conditions.append(Memory.year >= from_date.year)
    if to_date:
        conditions.append(Memory.year <= to_date.year)
    if created_by:
        conditions.append(Memory.created_by == created_by)

    result = await db.execute(
        select(Memory)
        .where(and_(*conditions))
        .options(selectinload(Memory.recall_logs))
        .order_by(Memory.created_at.desc())
    )
    memories = result.scalars().all()

    return [{"memory": _to_signed(m), "has_badge": _has_badge(m)} for m in memories]


async def get_memory(
    db: AsyncSession, memory_id: uuid_lib.UUID, current_user
) -> dict:
    membership = await _get_membership(db, current_user.id)
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="그룹에 소속되어 있지 않습니다.")

    memory = await _get_memory_or_404(db, memory_id)

    if memory.group_id != membership.group_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="접근 권한이 없습니다.")

    return {"memory": _to_signed(memory), "has_badge": _has_badge(memory)}


async def update_memory(
    db: AsyncSession, memory_id: uuid_lib.UUID, body: MemoryUpdateRequest, current_user
) -> dict:
    memory = await _get_memory_or_404(db, memory_id)

    if memory.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="수정 권한이 없습니다.")

    membership = await _get_membership(db, current_user.id)

    if body.image_key is not None:
        _validate_temp_key(body.image_key, "images")
        old_key = object_key_from_url(memory.image_url)
        memory.image_url = await _move_to_permanent(body.image_key, "images", membership.group_id)
        await delete_object(old_key)

    if body.voice_key is not None:
        if body.voice_key == "":
            # 빈 문자열 = 음성 삭제
            if memory.voice_url:
                await delete_object(object_key_from_url(memory.voice_url))
            memory.voice_url = None
        else:
            _validate_temp_key(body.voice_key, "voices")
            if memory.voice_url:
                await delete_object(object_key_from_url(memory.voice_url))
            memory.voice_url = await _move_to_permanent(body.voice_key, "voices", membership.group_id)

    if body.title is not None:
        memory.title = body.title
    if body.year is not None:
        memory.year = body.year
    if body.location is not None:
        memory.location = body.location
    if body.people is not None:
        memory.people = body.people
    if body.story is not None:
        memory.story = body.story

    db.add(memory)
    await db.flush()

    return {"memory": _to_signed(memory), "has_badge": _has_badge(memory)}


async def delete_memory(
    db: AsyncSession, memory_id: uuid_lib.UUID, current_user
) -> None:
    memory = await _get_memory_or_404(db, memory_id)

    if memory.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="삭제 권한이 없습니다.")

    await delete_object(object_key_from_url(memory.image_url))
    if memory.voice_url:
        await delete_object(object_key_from_url(memory.voice_url))

    await db.delete(memory)
