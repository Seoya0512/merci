from fastapi import APIRouter, Depends, HTTPException
from app.upload.schema import PresignedUrlRequest, PresignedUrlResponse
from app.core.dependencies import get_current_user
from app.models import User

router = APIRouter()


@router.post("/presigned-url", response_model=PresignedUrlResponse)
async def get_presigned_url(
    body: PresignedUrlRequest,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented")
