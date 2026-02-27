from fastapi import APIRouter, HTTPException
from app.auth.schema import KakaoCallbackRequest, NaverCallbackRequest, TokenResponse

router = APIRouter()


@router.post("/kakao/callback", response_model=TokenResponse)
async def kakao_callback(body: KakaoCallbackRequest):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/naver/callback", response_model=TokenResponse)
async def naver_callback(body: NaverCallbackRequest):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/logout", status_code=204)
async def logout():
    raise HTTPException(status_code=501, detail="Not implemented")
