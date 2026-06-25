from fastapi.testclient import TestClient
from psycopg import AsyncConnection
import json


async def test_booking_cancel_seated(
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

    # cancel user 1's seated booking (seats A1 + A2)
    booking_id = "b-10000000-0000-0000-0000-000000000002"

    response = test_client.post(f"/bookings/{booking_id}/cancel")
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == booking_id
    assert data["status"] == "cancelled"

    # the two seats held by the booking are available again
    cursor = await db_session.execute(
        "SELECT seat_number, is_available FROM seats "
        "WHERE id = ANY(%s) ORDER BY seat_number",
        ([
            "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        ],)
    )
    rows = await cursor.fetchall()
    assert [r["seat_number"] for r in rows] == ["A1", "A2"]
    assert all(r["is_available"] is True for r in rows)

    # the booking_seats rows for the cancelled booking are gone
    cursor = await db_session.execute(
        "SELECT COUNT(*) AS count FROM booking_seats WHERE booking_id = %s",
        ("10000000-0000-0000-0000-000000000002",)
    )
    row = await cursor.fetchone()
    assert row["count"] == 0

    # the event's available tickets get increased
    cursor = await db_session.execute(
        """
        SELECT available_tickets FROM events
        WHERE id = %s
        """,
        ("22222222-2222-2222-2222-222222222222",)
    )
    row = await cursor.fetchone()
    assert row['available_tickets'] == 1000  # were 998 before, 2 tickets got cancelled


async def test_booking_cancel_open_field(
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

    # cancel user 1's open-field booking
    booking_id = "b-10000000-0000-0000-0000-000000000001"

    response = test_client.post(f"/bookings/{booking_id}/cancel")
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 200
    assert data["id"] == booking_id
    assert data["status"] == "cancelled"

    # the event's available tickets get increased
    cursor = await db_session.execute(
        """
        SELECT available_tickets FROM events
        WHERE id = %s
        """,
        ("11111111-1111-1111-1111-111111111111",)
    )
    row = await cursor.fetchone()
    assert row['available_tickets'] == 9999  # were 9997 before, 2 tickets got cancelled


async def test_booking_cancel_open_field_not_own(
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

    # try to cancel user 2's open-field booking
    booking_id = "b-10000000-0000-0000-0000-000000000003"

    response = test_client.post(f"/bookings/{booking_id}/cancel")
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 403  # not allowed to cancel another's user booking
    assert data['detail'] == "You are not allowed to cancel this booking"



async def test_booking_cancel_twice(
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

    # cancel user 1's open-field booking
    booking_id = "b-10000000-0000-0000-0000-000000000001"

    response = test_client.post(f"/bookings/{booking_id}/cancel")
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 200
    assert data["id"] == booking_id
    assert data["status"] == "cancelled"

    # Cancel again
    response = test_client.post(f"/bookings/{booking_id}/cancel")
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 400
    assert data['detail'] == "Booking already cancelled"

