import secrets
import uuid
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import service
from app.auth.schema import (
    KakaoAuthUrlResponse,
    KakaoCallbackRequest,
    NaverAuthUrlResponse,
    NaverCallbackRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.core.config import settings
from app.core.database import get_db
from app.core.redis import get_redis
from app.core.security import create_access_token, create_refresh_token

router = APIRouter()


@router.get("/kakao/authorize", response_model=KakaoAuthUrlResponse)
async def kakao_auth_url():
    """프론트엔드가 유저를 리다이렉트할 카카오 로그인 URL을 반환합니다."""
    params = urlencode({
        "response_type": "code",
        "client_id": settings.KAKAO_CLIENT_ID,
        "redirect_uri": settings.KAKAO_REDIRECT_URI,
    })
    url = f"https://kauth.kakao.com/oauth/authorize?{params}"
    return KakaoAuthUrlResponse(url=url)


@router.post("/kakao/login", response_model=TokenResponse)
async def kakao_login(
    body: KakaoCallbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    프론트엔드에서 전달받은 code로 카카오 로그인을 처리합니다.
    1. code → 카카오 access_token 교환
    2. 카카오 access_token → 유저 프로필 조회
    3. DB에서 유저 조회 또는 자동 회원가입
    4. 서비스 JWT + Refresh Token 발급 후 반환
    """
    try:
        kakao_token = await service.issue_kakao_token(body.code)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"카카오 토큰 발급 실패: {e}",
        )

    try:
        profile = await service.get_kakao_user_info(kakao_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"카카오 프로필 조회 실패: {e}",
        )

    kakao_account = profile.get("kakao_account", {})
    user = await service.get_or_create_user(
        db=db,
        provider="kakao",
        provider_user_id=str(profile["id"]),
        email=kakao_account.get("email", ""),
        name=kakao_account.get("profile", {}).get("nickname", ""),
    )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token()
    await service.save_refresh_token(get_redis(), user.id, refresh_token)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.get("/naver/authorize", response_model=NaverAuthUrlResponse)
async def naver_auth_url():
    """프론트엔드가 유저를 리다이렉트할 네이버 로그인 URL을 반환합니다."""
    state = secrets.token_urlsafe(16)
    params = urlencode({
        "response_type": "code",
        "client_id": settings.NAVER_CLIENT_ID,
        "redirect_uri": settings.NAVER_REDIRECT_URI,
        "state": state,
    })
    url = f"https://nid.naver.com/oauth2.0/authorize?{params}"
    return NaverAuthUrlResponse(url=url, state=state)


@router.post("/naver/login", response_model=TokenResponse)
async def naver_login(
    body: NaverCallbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    프론트엔드에서 전달받은 code와 state로 네이버 로그인을 처리합니다.
    1. code → 네이버 access_token 교환
    2. 네이버 access_token → 유저 프로필 조회
    3. DB에서 유저 조회 또는 자동 회원가입
    4. 서비스 JWT + Refresh Token 발급 후 반환
    """
    try:
        naver_token = await service.issue_naver_token(body.code, body.state)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"네이버 토큰 발급 실패: {e}",
        )

    try:
        profile = await service.get_naver_user_info(naver_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"네이버 프로필 조회 실패: {e}",
        )

    user = await service.get_or_create_user(
        db=db,
        provider="naver",
        provider_user_id=profile["id"],
        email=profile.get("email", ""),
        name=profile.get("name", ""),
    )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token()
    await service.save_refresh_token(get_redis(), user.id, refresh_token)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshTokenRequest):
    """
    Refresh Token으로 새 Access Token을 발급합니다.
    Refresh Token의 TTL은 갱신되지 않으며, 만료 시 재로그인이 필요합니다.
    """
    redis = get_redis()
    user_id_str = await service.get_user_id_by_refresh_token(redis, body.refresh_token)

    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않거나 만료된 Refresh Token입니다.",
        )

    access_token = create_access_token(uuid.UUID(user_id_str))
    return TokenResponse(access_token=access_token, refresh_token=body.refresh_token)


@router.post("/logout", status_code=204)
async def logout(body: RefreshTokenRequest):
    """
    로그아웃 처리.
    Redis에서 Refresh Token을 삭제합니다.
    클라이언트는 응답 수신 후 저장된 access_token과 refresh_token을 모두 삭제해야 합니다.
    """
    await service.delete_refresh_token(get_redis(), body.refresh_token)
