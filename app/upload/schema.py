from pydantic import BaseModel
from enum import Enum


class FileType(str, Enum):
    IMAGE = "image"
    VOICE = "voice"


class PresignedUrlRequest(BaseModel):
    file_type: FileType
    content_type: str  # 예: "image/jpeg", "audio/mp4"


class PresignedUrlResponse(BaseModel):
    upload_url: str   # presigned PUT URL (temp 경로, 15분 유효)
    object_key: str   # 예: "temp/images/550e8400.jpg" — POST /memories 에 전달
