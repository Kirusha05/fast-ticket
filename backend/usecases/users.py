from psycopg import AsyncConnection
from repositories.users import UsersRepository
from models import User, UserRole
from fastapi import HTTPException

class UsersUseCase:
    def __init__(self, db_session: AsyncConnection):
        self.db_session = db_session
        self.users_repository = UsersRepository(db_session)

    async def get_all_users(self) -> list[User]:
        users = await self.users_repository.get_all()
        return users

    async def create_user(self, email, name, auth0_id) -> User:
        if await self.users_repository.get_by_email(email):
            raise HTTPException(status_code=400, detail="User with this email already exists.")

        new_user = User(
            id=User.generate_entity_id(),
            name=name,
            email=email,
            auth0_id=auth0_id,
            role=UserRole.USER
        )
        created_user = await self.users_repository.create(new_user)
        return created_user

    async def get_by_auth0_id(self, auth0_id: str):
        user = await self.users_repository.get_by_auth0_id(auth0_id)
        return user