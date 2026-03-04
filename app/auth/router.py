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
from app.core.dependencies import get_db
from app.core.redis import get_redis
from app.core.responses import AUTH_RESPONSES, BAD_REQUEST
from app.core.security import create_access_token, create_refresh_token

router = APIRouter()


@router.get(
    "/kakao/authorize",
    response_model=KakaoAuthUrlResponse,
    summary="카카오 로그인 URL 조회",
)
async def kakao_auth_url():
    """
    프론트엔드가 유저를 리다이렉트할 카카오 OAuth 로그인 URL을 반환합니다.

    반환된 `url` 로 유저를 리다이렉트하면 카카오 로그인 페이지로 이동합니다.
    로그인 완료 후 카카오는 설정된 `redirect_uri` 로 `code` 파라미터를 전달합니다.
    해당 `code` 를 `POST /auth/kakao/login` 에 전달하세요.
    """
    params = urlencode({
        "response_type": "code",
        "client_id": settings.KAKAO_CLIENT_ID,
        "redirect_uri": settings.KAKAO_REDIRECT_URI,
    })
    url = f"https://kauth.kakao.com/oauth/authorize?{params}"
    return KakaoAuthUrlResponse(url=url)


@router.post(
    "/kakao/login",
    response_model=TokenResponse,
    summary="카카오 로그인",
    responses=BAD_REQUEST,
)
async def kakao_login(
    body: KakaoCallbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    카카오 OAuth `code` 로 로그인을 처리하고 로그인을 처리하고 서비스 JWT(Access Token)과 Refresh Token을 발급합니다.

    이후 모든 API 요청에는 `Authorization: Bearer {access_token}` 헤더를 포함하세요.
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
    nickname = kakao_account.get("profile", {}).get("nickname", "")
    user = await service.get_or_create_user(
        db=db,
        provider="kakao",
        provider_user_id=str(profile["id"]),
        email=kakao_account.get("email", ""),
        name=nickname,
        nickname=nickname,
    )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token()
    await service.save_refresh_token(get_redis(), user.id, refresh_token)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.get(
    "/naver/authorize",
    response_model=NaverAuthUrlResponse,
    summary="네이버 로그인 URL 조회",
)
async def naver_auth_url():
    """
    프론트엔드가 유저를 리다이렉트할 네이버 OAuth 로그인 URL을 반환합니다.

    반환된 url로 유저를 리다이렉트하면 네이버 로그인 페이지로 이동합니다.

    로그인 완료 후 네이버는 설정된 `redirect_uri` 로 `code` 와 `state` 파라미터를 전달합니다.

    해당 값들을 `POST /auth/naver/login` 에 전달하세요.
    """
    state = secrets.token_urlsafe(16)
    params = urlencode({
        "response_type": "code",
        "client_id": settings.NAVER_CLIENT_ID,
        "redirect_uri": settings.NAVER_REDIRECT_URI,
        "state": state,
    })
    url = f"https://nid.naver.com/oauth2.0/authorize?{params}"
    return NaverAuthUrlResponse(url=url, state=state)


@router.post(
    "/naver/login",
    response_model=TokenResponse,
    summary="네이버 로그인",
    responses=BAD_REQUEST,
)
async def naver_login(
    body: NaverCallbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    네이버 OAuth `code` + `state` 로 로그인을 처리하고 서비스 JWT(Access Token)과 Refresh Token을 발급합니다.

    이후 모든 API 요청에는 `Authorization: Bearer {access_token}` 헤더를 포함하세요.
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
        nickname=profile.get("name", ""),
    )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token()
    await service.save_refresh_token(get_redis(), user.id, refresh_token)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Access Token 재발급",
    responses={401: AUTH_RESPONSES[401]},
)
async def refresh(body: RefreshTokenRequest):
    """
    Refresh Token으로 새 Access Token을 재발급합니다.

    - Refresh Token의 만료 시간은 갱신되지 않습니다.
    - Refresh Token이 만료된 경우 재로그인이 필요합니다.
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


@router.post(
    "/logout",
    status_code=204,
    summary="로그아웃",
)
async def logout(body: RefreshTokenRequest):
    """
    로그아웃 처리를 합니다.

    Redis에서 Refresh Token을 삭제합니다.
    클라이언트는 응답 수신 후 저장된 `access_token` 과 `refresh_token` 을 모두 삭제해야 합니다.
    """
    await service.delete_refresh_token(get_redis(), body.refresh_token)
