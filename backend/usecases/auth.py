from psycopg import AsyncConnection
from repositories.users import UsersRepository
from fastapi import Response
from models.auth import LoginRequest, LoginResponse, LogoutResponse


class AuthUseCase:
    def __init__(self, db_session: AsyncConnection):
        self.db_session = db_session
        self.users_repository = UsersRepository(db_session)

    async def login(self, login_request: LoginRequest, response: Response) -> LoginResponse:
        user = await self.users_repository.get_by_email(login_request.email)
        return LoginResponse(message="Login successful", user_id=user.id)

    async def logout(self, response: Response) -> LoginResponse:
        return LogoutResponse(message="Logged out successfully")