from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.models import User

router = APIRouter()

# F-08 사진 업로드
@router.post("")
async def upload_memory(current_user: User = Depends(get_current_user)):
    # TODO: 이미지 + 설명 + 음성 업로드
    pass

# F-09 사진 목록 조회
@router.get("")
async def list_memories(current_user: User = Depends(get_current_user)):
    # TODO: 그룹 단위 목록 조회
    pass

# F-10 사진 상세 보기
@router.get("/{memory_id}")
async def get_memory(memory_id: int, current_user: User = Depends(get_current_user)):
    # TODO: 상세 조회
    pass
