from fastapi import APIRouter, Depends
from usecases.users import UsersUseCase
from config.db_session import get_db_session
from routes.deps.auth import get_current_user


router = APIRouter()

@router.get("/")
async def get_all_users(db=Depends(get_db_session)):
    users_use_case = UsersUseCase(db)
    return await users_use_case.get_all_users()


@router.get("/profile")
async def get_profile(
    # db=Depends(get_db_session),
    user=Depends(get_current_user)
):
    return user
    
