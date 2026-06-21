from psycopg import AsyncConnection
from models.base import EntityId
from repositories.users import UsersRepository
from models.user import User, CreateUserRequest
from models.user import UpdateUserRequest
from fastapi import HTTPException


class UsersUseCase:
    def __init__(self, db_session: AsyncConnection):
        self.db_session = db_session
        self.users_repository = UsersRepository(db_session)

    async def create_user(self, user: CreateUserRequest) -> User:
        if await self.users_repository.get_by_email(user.email):
            raise HTTPException(status_code=400, detail="User with this email already exists.")

        new_user = User(
            id=User.generate_entity_id(),
            name=user.name,
            email=user.email,
            auth0_id=None
        )

        created_user = await self.users_repository.create(new_user)
        return created_user

    # Not realistic for user, but kept for future CRUD ops
    async def get_user(self, user_id: EntityId) -> User:
        user = await self.users_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
        return user

    async def get_all_users(self) -> User:
        users = await self.users_repository.get_all()
        return users

    async def update_user(self, current_user_id: EntityId, target_user_id: EntityId, new_user: UpdateUserRequest) -> User:
        if current_user_id != target_user_id:
            raise HTTPException(status_code=403, detail="You are not allowed to update this user")

        user = await self.users_repository.get_by_id(target_user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with id {target_user_id} not found")

        user.name = new_user.name
        updated_user = await self.users_repository.update(target_user_id, user)
        if not updated_user:
            raise HTTPException(status_code=404, detail=f"User with id {target_user_id} not found")
        
        return updated_user

    async def delete_user(self, current_user_id: EntityId, target_user_id: EntityId):
        if current_user_id != target_user_id:
            raise HTTPException(status_code=403, detail="You are not allowed to delete this user")
        
        await self.users_repository.delete(target_user_id)
        # return {"message": "Deleted successfully"}