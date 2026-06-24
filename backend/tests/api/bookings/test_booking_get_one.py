from fastapi.testclient import TestClient
from psycopg import AsyncConnection
import json


async def test_booking_get_own(
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

    # fetch user 1's open-field booking
    booking_id = "b-10000000-0000-0000-0000-000000000002"

    response = test_client.get(f"/bookings/{booking_id}")
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 200
    assert data["id"] == booking_id
    assert data["user_id"] == "u-11111111-1111-1111-1111-111111111111"
    assert data["event_id"] == "e-22222222-2222-2222-2222-222222222222"
    assert data["status"] == "confirmed"
    assert data["ticket_count"] == 2
    assert len(data["booking_seats"]) == 2


async def test_booking_get_not_own(
    test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy
):
    # Insert test data: two users, events, seats and three bookings
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

    # try to fetch user 2's booking
    booking_id = "b-10000000-0000-0000-0000-000000000003"

    response = test_client.get(f"/bookings/{booking_id}")
    data = response.json()

    assert response.status_code == 403
    assert data["detail"] == "You are not allowed to view this booking"