import uuid
from datetime import timedelta

import httpx
from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models import User

_REFRESH_PREFIX = "refresh:"


async def save_refresh_token(redis: Redis, user_id: uuid.UUID, token: str) -> None:
    await redis.setex(
        f"{_REFRESH_PREFIX}{token}",
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        str(user_id),
    )


async def get_user_id_by_refresh_token(redis: Redis, token: str) -> str | None:
    return await redis.get(f"{_REFRESH_PREFIX}{token}")


async def delete_refresh_token(redis: Redis, token: str) -> None:
    await redis.delete(f"{_REFRESH_PREFIX}{token}")


async def issue_naver_token(code: str, state: str) -> str:
    """네이버 접근 토큰 발급 요청"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://nid.naver.com/oauth2.0/token",
            params={
                "grant_type": "authorization_code",
                "client_id": settings.NAVER_CLIENT_ID,
                "client_secret": settings.NAVER_CLIENT_SECRET,
                "code": code,
                "state": state,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    if "error" in data:
        raise ValueError(data.get("error_description", data["error"]))

    return data["access_token"]


async def get_naver_user_info(naver_access_token: str) -> dict:
    """네이버 access_token으로 유저 프로필 조회"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://openapi.naver.com/v1/nid/me",
            headers={"Authorization": f"Bearer {naver_access_token}"},
        )
        resp.raise_for_status()
        data = resp.json()

    if data.get("resultcode") != "00":
        raise ValueError(data.get("message", "네이버 프로필 조회 실패"))

    return data["response"]


async def issue_kakao_token(code: str) -> str:
    """카카오 접근 토큰 발급 요청"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://kauth.kakao.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": settings.KAKAO_CLIENT_ID,
                "client_secret": settings.KAKAO_CLIENT_SECRET,
                "redirect_uri": settings.KAKAO_REDIRECT_URI,
                "code": code,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    if "error" in data:
        raise ValueError(data.get("error_description", data["error"]))

    return data["access_token"]


async def get_kakao_user_info(kakao_access_token: str) -> dict:
    """카카오 access_token으로 유저 프로필 조회"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {kakao_access_token}"},
        )
        resp.raise_for_status()

    return resp.json()


_PROVIDER_DISPLAY_NAME = {
    "kakao": "카카오",
    "naver": "네이버",
}


async def get_or_create_user(
    db: AsyncSession,
    provider: str,
    provider_user_id: str,
    email: str,
    name: str,
    nickname: str,
) -> User:
    # 동일 provider + provider_user_id로 기존 유저 조회 (일반 로그인)
    result = await db.execute(
        select(User).where(
            User.provider == provider,
            User.provider_user_id == provider_user_id,
        )
    )
    user = result.scalar_one_or_none()
    if user is not None:
        return user

    # 동일 이메일로 다른 provider 가입 여부 확인
    if email:
        result = await db.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()
        if existing is not None:
            existing_provider = _PROVIDER_DISPLAY_NAME.get(existing.provider, existing.provider)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{existing_provider}로 이미 가입하셨어요. {existing_provider}로 로그인해 주세요.",
            )

    user = User(
        id=uuid.uuid4(),
        provider=provider,
        provider_user_id=provider_user_id,
        email=email,
        name=name,
        nickname=nickname,
    )
    db.add(user)
    return user
