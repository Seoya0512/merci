from fastapi import APIRouter, Depends, HTTPException
from app.upload.schema import PresignedUrlRequest, PresignedUrlResponse
from app.core.dependencies import get_current_user
from app.core.responses import AUTH_RESPONSES, BAD_REQUEST
from app.models import User

router = APIRouter()


@router.post(
    "/presigned-url",
    response_model=PresignedUrlResponse,
    summary="Presigned URL 발급",
    description="클라이언트가 Cloudflare R2에 파일을 직접 업로드할 수 있는 Presigned URL을 발급합니다.",
    responses={**AUTH_RESPONSES, **BAD_REQUEST},
)
async def get_presigned_url(
    body: PresignedUrlRequest,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")
