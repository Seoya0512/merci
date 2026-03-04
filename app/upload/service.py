import uuid

from fastapi import HTTPException

from app.core.storage import generate_presigned_url
from app.upload.schema import FileType, PresignedUrlResponse

ALLOWED_CONTENT_TYPES: dict[FileType, dict[str, str]] = {
    FileType.IMAGE: {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    },
    FileType.VOICE: {
        "audio/mpeg": ".mp3",
        "audio/mp4": ".m4a",
        "audio/webm": ".webm",
    },
}


def create_presigned_url(file_type: FileType, content_type: str) -> PresignedUrlResponse:
    allowed = ALLOWED_CONTENT_TYPES.get(file_type, {})
    ext = allowed.get(content_type)
    if ext is None:
        raise HTTPException(
            status_code=400,
            detail=f"허용되지 않는 content_type입니다. 허용: {list(allowed.keys())}",
        )

    object_key = f"temp/{file_type.value}s/{uuid.uuid4()}{ext}"
    upload_url = generate_presigned_url(object_key, content_type)

    return PresignedUrlResponse(upload_url=upload_url, object_key=object_key)
