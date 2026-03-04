from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime


class MemoryCreateRequest(BaseModel):
    title: str = Field(..., description="추억 제목")
    image_key: str = Field(..., description="POST /uploads/presigned-url 에서 받은 object_key (예: temp/images/uuid.jpg)")
    year: int = Field(..., description="추억이 있었던 연도 (예: 1985)")
    location: str = Field(..., description="장소 (예: 서울 성북구)")
    people: str = Field(..., description="함께한 사람들 (예: 엄마, 아빠, 나)")
    story: str = Field(..., description="추억 이야기")
    voice_key: str | None = Field(None, description="음성 object_key (예: temp/voices/uuid.m4a). 없으면 생략")


class MemoryUpdateRequest(BaseModel):
    title: str | None = Field(None, description="수정할 제목. 생략 시 변경 없음")
    image_key: str | None = Field(
        None,
        description="이미지 교체 시 새 object_key 전달. 생략 시 기존 이미지 유지",
    )
    year: int | None = Field(None, description="수정할 연도. 생략 시 변경 없음")
    location: str | None = Field(None, description="수정할 장소. 생략 시 변경 없음")
    people: str | None = Field(None, description="수정할 인물. 생략 시 변경 없음")
    story: str | None = Field(None, description="수정할 이야기. 생략 시 변경 없음")
    voice_key: str | None = Field(
        None,
        description=(
            "음성 변경/삭제. "
            "새 음성으로 교체하려면 새 object_key 전달. "
            '음성을 삭제하려면 빈 문자열("")을 전달. '
            "생략 시 기존 음성 유지"
        ),
    )


class MemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    group_id: UUID
    title: str
    image_url: str = Field(..., description="사진 URL (presigned GET URL, 1시간 유효)")
    year: int
    location: str
    people: str
    story: str
    voice_url: str | None = Field(None, description="음성 URL (presigned GET URL, 1시간 유효). 음성이 없으면 null")
    created_by: UUID
    created_at: datetime
    has_badge: bool = Field(False, description="'기억하심' 회상 기록이 1건 이상 있으면 true")
