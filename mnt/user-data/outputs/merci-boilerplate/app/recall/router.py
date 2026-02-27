from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.models import User

router = APIRouter()

# F-11 기억 여부 기록
@router.post("/{memory_id}/recalls")
async def create_recall_log(memory_id: int, current_user: User = Depends(get_current_user)):
    # TODO: 기억 여부 저장 + 마씨 배지 여부 판단
    # result == "기억하셨어요" 일 때만 배지
    pass
