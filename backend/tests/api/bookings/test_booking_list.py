from fastapi.testclient import TestClient
from psycopg import AsyncConnection
import json


async def test_booking_list_for_user(
    test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy
):
    # Insert test data: two users, events, seats and three bookings (two for user 1)
    with open('tests/data/user.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/seats.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/booking.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    override_current_user_dummy()  # bypass authorization, logged in as user 1

    response = test_client.get("/bookings/")
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 200
    assert len(data) == 2

    returned_ids = {b["id"] for b in data}
    assert returned_ids == {
        "b-10000000-0000-0000-0000-000000000001",
        "b-10000000-0000-0000-0000-000000000002",
    }

    # all returned bookings belong to the current user (user 1)
    user_id = "u-11111111-1111-1111-1111-111111111111"
    assert all(b["user_id"] == user_id for b in data)
    assert all(b["status"] == "confirmed" for b in data)
