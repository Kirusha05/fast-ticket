from fastapi.testclient import TestClient
from psycopg import AsyncConnection


async def test_user_get_me(
    test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy
):
    """
    Setup:
      Users:
        - User 1 (u-11111111-...), "Test User"
        - User 2 (u-22222222-...), "Second User"

    Logged in as User 1.
    """
    with open('tests/data/user.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    override_current_user_dummy()  # bypass authorization, logged in as user 1

    response = test_client.get("/users/me")
    data = response.json()

    assert response.status_code == 200
    assert data['name'] == 'Test User'
