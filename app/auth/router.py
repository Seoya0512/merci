from fastapi import APIRouter, HTTPException
from app.auth.schema import KakaoCallbackRequest, NaverCallbackRequest, TokenResponse
from app.core.responses import AUTH_RESPONSES, BAD_REQUEST

router = APIRouter()


@router.post(
    "/kakao/callback",
    response_model=TokenResponse,
    summary="카카오 OAuth 로그인",
    description="카카오 인증 코드로 로그인하고 JWT를 발급합니다. 신규 유저는 자동 회원가입됩니다.",
    responses={**BAD_REQUEST},
)
async def kakao_callback(body: KakaoCallbackRequest):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post(
    "/naver/callback",
    response_model=TokenResponse,
    summary="네이버 OAuth 로그인",
    description="네이버 인증 코드로 로그인하고 JWT를 발급합니다. 신규 유저는 자동 회원가입됩니다.",
    responses={**BAD_REQUEST},
)
async def naver_callback(body: NaverCallbackRequest):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post(
    "/logout",
    status_code=204,
    summary="로그아웃",
    description="현재 사용자의 세션을 종료합니다.",
    responses={**AUTH_RESPONSES},
)
async def logout():
    raise HTTPException(status_code=501, detail="Not implemented")
