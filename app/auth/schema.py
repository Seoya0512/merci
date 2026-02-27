from pydantic import BaseModel


class KakaoCallbackRequest(BaseModel):
    code: str


class NaverCallbackRequest(BaseModel):
    code: str
    state: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
