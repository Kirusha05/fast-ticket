from fastapi.testclient import TestClient
from psycopg import AsyncConnection
import json


async def test_booking_create_open_field(test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy):
    # Insert test data
    with open('tests/data/user.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    override_current_user_dummy()  # bypass authorization
    user_id = "u-11111111-1111-1111-1111-111111111111"
    event_id = "e-11111111-1111-1111-1111-111111111111"

    request = {
        "event_id": event_id,
        "ticket_count": 2
    }

    response = test_client.post("/bookings/", json=request)
    data = response.json()
    # print(json.dumps(data, indent=2))

    assert response.status_code == 201
    assert data["id"] is not None
    assert data["user_id"] == user_id
    assert data["event_id"] == event_id
    assert data["status"] == "confirmed"
    assert data["ticket_count"] == 2
    assert len(data["booking_seats"]) == 0
    assert data["created_at"] is not None
    assert data["updated_at"] is not None

    cursor = await db_session.execute(
        """
        SELECT available_tickets FROM events
        WHERE id = %s
        """,
        (event_id.removeprefix('e-'),)
    )
    row = await cursor.fetchone()
    assert row['available_tickets'] == 9998


async def test_booking_create_seated(test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy):
    # Insert test data: user, seated event and its seats
    with open('tests/data/user.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/seats.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    override_current_user_dummy()  # bypass authorization
    user_id = "u-11111111-1111-1111-1111-111111111111"
    event_id = "e-22222222-2222-2222-2222-222222222222"
    seat_ids = [
        "s-aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "s-bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    ]

    request = {
        "event_id": event_id,
        "seat_ids": seat_ids
    }

    response = test_client.post("/bookings/", json=request)
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 201
    assert data["id"] is not None
    assert data["user_id"] == user_id
    assert data["event_id"] == event_id
    assert data["status"] == "confirmed"
    assert data["ticket_count"] == 2
    assert len(data["booking_seats"]) == 2
    assert data["created_at"] is not None
    assert data["updated_at"] is not None

    # the two booked seats are returned on the booking
    booked = {s["seat_number"] for s in data["booking_seats"]}
    assert booked == {"A1", "A2"}

    # and persisted as unavailable in the DB
    cursor = await db_session.execute(
        "SELECT seat_number, is_available FROM seats "
        "WHERE id = ANY(%s) ORDER BY seat_number",
        ([seat_id.removeprefix("s-") for seat_id in seat_ids],)
    )
    rows = await cursor.fetchall()
    assert [r["seat_number"] for r in rows] == ["A1", "A2"]
    assert all(r["is_available"] is False for r in rows)