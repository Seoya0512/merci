from fastapi import APIRouter, Depends
from app.upload.schema import PresignedUrlRequest, PresignedUrlResponse
from app.upload.service import create_presigned_url
from app.core.dependencies import get_current_user
from app.models import User

router = APIRouter()


@router.post(
    "/presigned-url",
    response_model=PresignedUrlResponse,
    summary="파일 업로드용 Presigned URL 발급",
)
async def get_presigned_url(
    body: PresignedUrlRequest,
    current_user: User = Depends(get_current_user),
):
    """
    사진 또는 음성 파일을 Cloudflare R2에 직접 업로드하기 위한 서명된 URL을 발급합니다.

    **전체 업로드 흐름**

    ```
    1. API로 업로드용 presigned URL 및 object_key 발급

    2. 발급받은 upload_url 로 파일 직접 업로드 (서버 미경유)
       PUT {upload_url}
       Content-Type: image/jpeg   ← 발급 시 지정한 content_type과 반드시 일치
       Body: (파일 바이너리)

       → 200 OK

    3. 추억 등록 시 object_key 전달
       POST /memories
       { "image_key": "temp/images/550e8400-....jpg", ... }
    ```

    **주의사항**
    - `upload_url` 은 **15분** 후 만료됩니다.
    - PUT 요청의 Content-Type 헤더는 발급 시 지정한 content_type 과 **정확히 일치**해야 합니다.
      불일치 시 R2가 `SignatureDoesNotMatch` 오류를 반환합니다.
    - PUT 요청에 `Authorization` 헤더를 포함하지 마세요. 인증 정보는 URL에 이미 포함되어 있습니다.
    - 파일을 업로드한 뒤 `POST /memories` 를 호출하지 않으면, R2 Lifecycle Rule에 의해
      **24시간 후 자동 삭제**됩니다.

    **허용 파일 타입**
    - 사진: `image/jpeg`, `image/png`, `image/webp`
    - 음성: `audio/mpeg` (.mp3), `audio/mp4` (.m4a), `audio/webm`
    """
    return create_presigned_url(body.file_type, body.content_type)
