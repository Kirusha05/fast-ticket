from psycopg import AsyncConnection
from repositories.users import UsersRepository
from models.user import User

class UsersUseCase:
    def __init__(self, db_session: AsyncConnection):
        self.db_session = db_session
        self.users_repository = UsersRepository(db_session)

    async def get_all_users(self) -> list[User]:
        users = await self.users_repository.get_all()
        return users