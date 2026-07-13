from fastapi import APIRouter, Depends
from routes.deps.auth import get_current_user


router = APIRouter()

@router.get("/me")
async def get_self_profile(
    user=Depends(get_current_user)
):
    return user