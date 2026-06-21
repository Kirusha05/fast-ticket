from fastapi import APIRouter, Depends
from usecases.users import UsersUseCase
from config.db_session import get_db_session
from models.user import CreateUserRequest, User, UpdateUserRequest
from routes.deps.auth import get_current_user
from models import EntityId


router = APIRouter()


@router.get("/")
async def get_all_users(db=Depends(get_db_session)):
    users_use_case = UsersUseCase(db)
    return await users_use_case.get_all_users()

# @router.get("/{user_id}")
# async def get_user(
#     user_id: str,
#     db=Depends(get_db_session)
# ) -> User:
#     user_id = EntityId.from_string(user_id)
#     users_use_case = UsersUseCase(db)
#     return await users_use_case.get_user(user_id)


# @router.post("/")
# async def create_user(
#     user: CreateUserRequest, db=Depends(get_db_session)
# ) -> User:
#     users_use_case = UsersUseCase(db)
#     result = await users_use_case.create_user(user)
#     return result


# @router.put("/{target_user_id}")
# async def update_user(
#     target_user_id: str,
#     new_user: UpdateUserRequest,
#     current_user_id=Depends(get_current_user_id),
#     db=Depends(get_db_session)
# ) -> User:
#     target_user_id = EntityId.from_string(target_user_id)
#     users_use_case = UsersUseCase(db)
#     result = await users_use_case.update_user(current_user_id, target_user_id, new_user)
#     return result


# @router.delete("/{target_user_id}")
# async def delete_user(
#     target_user_id: str,
#     current_user_id=Depends(get_current_user_id),
#     db=Depends(get_db_session)
# ):
#     target_user_id = EntityId.from_string(target_user_id)
#     users_use_case = UsersUseCase(db)
#     result =  await users_use_case.delete_user(current_user_id, target_user_id)
#     return result


@router.get("/profile")
async def get_profile(
    # db=Depends(get_db_session),
    user=Depends(get_current_user)
):
    return user
    
