from pydantic import BaseModel
from enum import Enum


class FileType(str, Enum):
    IMAGE = "image"
    VOICE = "voice"


class PresignedUrlRequest(BaseModel):
    file_type: FileType
    content_type: str  # 예: "image/jpeg", "audio/mp4"


class PresignedUrlResponse(BaseModel):
    upload_url: str  # S3 presigned PUT URL
    file_url: str    # 업로드 후 접근할 파일 URL
