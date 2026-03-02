from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.users.schema import UserUpdateRequest


async def update_user(db: AsyncSession, user: User, body: UserUpdateRequest) -> User:
    if body.nickname is not None:
        user.nickname = body.nickname
    db.add(user)
    return user
