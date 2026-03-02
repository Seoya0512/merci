def _err(description: str, code: str) -> dict:
    return {
        "description": description,
        "content": {
            "application/json": {
                "example": {"detail": code}
            }
        },
    }


# 인증 필요 엔드포인트 공통 응답
AUTH_RESPONSES = {
    401: _err("인증 필요 (토큰 없음 또는 만료)", "UNAUTHORIZED"),
    403: _err("접근 권한 없음", "FORBIDDEN"),
    500: _err("서버 내부 오류", "INTERNAL_SERVER_ERROR"),
}

BAD_REQUEST  = {400: _err("잘못된 요청 형식", "BAD_REQUEST")}
NOT_FOUND    = {404: _err("리소스를 찾을 수 없음", "NOT_FOUND")}
CONFLICT     = {409: _err("이미 존재하거나 충돌하는 요청", "CONFLICT")}
