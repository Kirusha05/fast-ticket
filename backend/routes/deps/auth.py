from fastapi import Request, HTTPException, Depends
import httpx
from jose import jwt, JWTError
from config import Mode, config
from config import get_db_session

from models import User
# from repositories import UsersRepository
from usecases import UsersUseCase

# Cache JWKS so we don't hit Auth0 on every request
# Keys rarely rotate; a server restart will refresh the cache if they do
_AUTH0_JWKS: dict | None = None

def _get_jwks() -> dict:
    global _AUTH0_JWKS
    if _AUTH0_JWKS is None:
        url = f"https://{config.AUTH0.DOMAIN}/.well-known/jwks.json"
        response = httpx.get(url, timeout=5)
        response.raise_for_status()
        _AUTH0_JWKS = response.json()
    return _AUTH0_JWKS


async def get_current_user(
    request: Request, db=Depends(get_db_session)
) -> User:
    # skip Auth0 tokens during load testing
    if config.MODE == Mode.LOAD_TEST:
        auth0_id = request.headers.get("X-Load-Test-User")

        if not auth0_id:
            print("Missing load test user")
            raise HTTPException(
                status_code=401,
                detail="Missing load test user",
            )

        users_use_case = UsersUseCase(db)
        user = await users_use_case.get_by_auth0_id(auth0_id)

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Load test user does not exist",
            )

        return user

    # 1. Extract the Bearer token
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    token = auth_header.removeprefix("Bearer ")

    # 2. Validate the JWT against Auth0's public keys
    try:
        payload = jwt.decode(
            token,
            key=_get_jwks(),
            algorithms=["RS256"],
            audience=config.AUTH0.AUDIENCE,
            issuer=f"https://{config.AUTH0.DOMAIN}/",
        )
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    auth0_id: str | None = payload.get("sub")  # e.g. "auth0|64f3a..."
    if not auth0_id:
        raise HTTPException(status_code=401, detail="Token missing sub claim")

    # 3. Find the DB user
    users_use_case = UsersUseCase(db)
    user = await users_use_case.get_by_auth0_id(auth0_id)

    if user:
        return user

    # Create new user if doesn't exist
    namespace = config.AUTH0.AUDIENCE
    email = payload.get(f"{namespace}/email")
    name = payload.get(f"{namespace}/name")

    created_user = await users_use_case.create_user(email, name, auth0_id)
    return created_user