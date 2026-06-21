from fastapi import APIRouter, Depends, Response
from usecases.auth import AuthUseCase
from config.db_session import get_db_session
from models.auth import LoginRequest, LoginResponse, LogoutResponse

router = APIRouter()


@router.post("/login")
async def login(
    login_request: LoginRequest,
    response: Response,
    db=Depends(get_db_session),
) -> LoginResponse:
    auth_use_case = AuthUseCase(db)
    return await auth_use_case.login(login_request, response)


@router.post("/logout")
async def logout(
    response: Response,
    db=Depends(get_db_session),
) -> LogoutResponse:
    auth_use_case = AuthUseCase(db)
    return await auth_use_case.logout(response)
