from pydantic import BaseModel


class KakaoCallbackRequest(BaseModel):
    code: str


class NaverCallbackRequest(BaseModel):
    code: str
    state: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class NaverAuthUrlResponse(BaseModel):
    url: str
    state: str


class KakaoAuthUrlResponse(BaseModel):
    url: str
