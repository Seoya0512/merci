from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.models import User

router = APIRouter()

# F-05 그룹 생성
@router.post("")
async def create_group(current_user: User = Depends(get_current_user)):
    # TODO: 그룹 생성 로직
    pass

# F-06 초대 코드로 그룹 참여
@router.post("/join")
async def join_group(current_user: User = Depends(get_current_user)):
    # TODO: 초대 코드 참여 로직
    pass

# F-07 초대 코드 조회 (OWNER만)
@router.get("/me/invite-code")
async def get_invite_code(current_user: User = Depends(get_current_user)):
    # TODO: 초대 코드 조회 로직
    pass
