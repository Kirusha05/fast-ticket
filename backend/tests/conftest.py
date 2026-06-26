import pytest
from main import app
from models import User, EntityId
from fastapi.testclient import TestClient
from psycopg import AsyncConnection
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from config.config import config
from routes.deps.auth import get_current_user

# run tests with this:
# MODE=test uv run pytest -v

# scopes:
# session -> package -> module -> class -> function

@pytest.fixture(scope='session')
def test_client():
    # initialize by context manager so the app can run its lifespan correctly
    with TestClient(app) as client:
        yield client


# create a DB connection pool for the tests
@pytest.fixture(scope='session')
async def db_pool() -> AsyncConnectionPool:
    if not config.DB.DATABASE.endswith("_test"):
        raise RuntimeError("DB_DATABASE name must end with _test")

    DB_POOL = AsyncConnectionPool(
        conninfo=config.DB.connection_string,
        min_size=config.DB.POOL_MIN_SIZE,
        max_size=config.DB.POOL_MAX_SIZE,
        open=False,
    )
    await DB_POOL.open()
    await DB_POOL.wait(5)
    return DB_POOL


# autouse=True ensures a clean DB state even if db_session fixture parameter is not used in the test_ function
@pytest.fixture(scope='function', autouse=True)
async def db_session(db_pool: AsyncConnectionPool) -> AsyncConnection:
    async with db_pool.connection() as conn:
        conn.row_factory = dict_row
        # yield the connection to the test function
        yield conn

        # rollback any uncommitted transactions if there were any
        await conn.rollback()

        # delete all data from the tables for cleanup
        models = [
            "booking_tiered_tickets",
            "booking_seated_tickets",
            "event_tiers",
            "event_seats",
            "bookings",
            "events",
            "users"
        ]
        for model in models:
            await conn.execute(f"DELETE FROM {model}")
        await conn.commit()

        # check everything is cleaned up
        for model in models:
            cursor = await conn.execute(f"SELECT COUNT(*) FROM {model}")
            result: dict = await cursor.fetchone()
            assert result['count'] == 0, f"Table {model} could not be cleaned up"
    

@pytest.fixture
def override_current_user_custom(test_client: TestClient):
    def _ovveride(user: User):
        app.dependency_overrides[get_current_user] = lambda: user
    yield _ovveride
    app.dependency_overrides.clear()


@pytest.fixture
def override_current_user_dummy(test_client: TestClient):
    user = User(
        id=EntityId.from_string("u-11111111-1111-1111-1111-111111111111"),
        name="Test User",
        email="test@test.com",
        auth0_id="ababababababab"
    )

    def _ovveride():
        app.dependency_overrides[get_current_user] = lambda: user
    yield _ovveride
    app.dependency_overrides.clear()