from fastapi.testclient import TestClient
from psycopg import AsyncConnection
import json


async def test_booking_cancel_seated_status_pending(
    test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy
):
    """
    Setup:
      Users:
        - User 1 (u-11111111-...), "Test User"
        - User 2 (u-22222222-...), "Second User"

      Events:
        - Summerfest (e-11111111-...), open_field, 10000 total/available
        - Opera Night (e-22222222-...), seated, 1000 available (took 2 -> 998)
        - Rock Arena (e-33333333-...), seated, 500 total/available

      Tiers (for Summerfest):
        - General (et-77777777-...), $50, 9997 available (was 10000, 3 taken)

      Seats (Opera Night):
        - A1 (es-aaaa...), $150, is_available = FALSE  <- taken by booking #2
        - A2 (es-bbbb...), $150, is_available = FALSE  <- taken by booking #2
        - B1 (es-cccc...), $120, is_available = TRUE

      Pre-existing bookings (all pending):
        #1 (b-10000000-...-001): User 1, Summerfest, 2x General @ $50 = $100
        #2 (b-10000000-...-002): User 1, Opera Night, A1+A2 @ $150 ea = $300
        #3 (b-10000000-...-003): User 2, Summerfest, 1x General @ $50

    Logged in as User 1.
    Cancel booking #2 (seated - A1 & A2 on Opera Night).
    """
    with open('tests/data/user.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/seats.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/tiers.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/booking_pending.sql') as f:
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
        "SELECT seat_number, is_available FROM event_seats "
        "WHERE id = ANY(%s) ORDER BY seat_number",
        ([
            "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        ],)
    )
    rows = await cursor.fetchall()
    assert [r["seat_number"] for r in rows] == ["A1", "A2"]
    assert all(r["is_available"] is True for r in rows)

    # the booking_seated_tickets rows for the cancelled booking are gone
    cursor = await db_session.execute(
        "SELECT COUNT(*) AS count FROM booking_seated_tickets WHERE booking_id = %s",
        ("10000000-0000-0000-0000-000000000002",)
    )
    row = await cursor.fetchone()
    assert row["count"] == 0

    # the event's available tickets get increased
    cursor = await db_session.execute(
        "SELECT available_tickets FROM events WHERE id = %s",
        ("22222222-2222-2222-2222-222222222222",)
    )
    row = await cursor.fetchone()
    assert row['available_tickets'] == 1000  # were 998 before, 2 tickets got cancelled


async def test_booking_cancel_open_field_status_pending(
    test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy
):
    """
    Setup:
      Users:
        - User 1 (u-11111111-...), "Test User"
        - User 2 (u-22222222-...), "Second User"

      Events:
        - Summerfest (e-11111111-...), open_field, 9997 available (was 10000, 3 taken)
        - Opera Night (e-22222222-...), seated, 998 available (was 1000, 2 taken)
        - Rock Arena (e-33333333-...), seated, 500 total/available

      Tiers (for Summerfest):
        - General (et-77777777-...), $50, 9997 available (was 10000, 3 taken)

      Pre-existing bookings (all pending):
        #1 (b-10000000-...-001): User 1, Summerfest, 2x General @ $50 = $100
        #2 (b-10000000-...-002): User 1, Opera Night, A1+A2 @ $150 ea = $300
        #3 (b-10000000-...-003): User 2, Summerfest, 1x General @ $50

    Logged in as User 1.
    Cancel booking #1 (open-field - 2 General tickets on Summerfest).
    """
    with open('tests/data/user.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/seats.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/tiers.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/booking_pending.sql') as f:
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
        "SELECT available_tickets FROM events WHERE id = %s",
        ("11111111-1111-1111-1111-111111111111",)
    )
    row = await cursor.fetchone()
    assert row['available_tickets'] == 9999  # were 9997 before, 2 tickets got cancelled

    # the tier's available tickets get increased
    cursor = await db_session.execute(
        "SELECT available_tickets FROM event_tiers WHERE id = %s",
        ("77777777-7777-7777-7777-777777777777",)
    )
    row = await cursor.fetchone()
    assert row['available_tickets'] == 9999  # were 9997 before, 2 tickets got cancelled

    # the booking_tiered_tickets rows for the cancelled booking are gone
    cursor = await db_session.execute(
        "SELECT COUNT(*) AS count FROM booking_tiered_tickets WHERE booking_id = %s",
        ("10000000-0000-0000-0000-000000000001",)
    )
    row = await cursor.fetchone()
    assert row["count"] == 0


async def test_booking_cancel_open_field_not_own(
    test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy
):
    """
    Setup:
      Users:
        - User 1 (u-11111111-...), "Test User"
        - User 2 (u-22222222-...), "Second User"

      Events:
        - Summerfest (e-11111111-...), open_field, 9997 available (was 10000, 3 taken)
        - Opera Night (e-22222222-...), seated, 998 available (was 1000, 2 taken)
        - Rock Arena (e-33333333-...), seated, 500 total/available

      Tiers (for Summerfest):
        - General (et-77777777-...), $50, 9997 available (was 10000, 3 taken)

      Pre-existing bookings (all pending):
        #1 (b-10000000-...-001): User 1, Summerfest, 2x General @ $50 = $100
        #2 (b-10000000-...-002): User 1, Opera Night, A1+A2 @ $150 ea = $300
        #3 (b-10000000-...-003): User 2, Summerfest, 1x General @ $50

    Logged in as User 1.
    Try to cancel booking #3 which belongs to User 2 -> reject with 403.
    """
    with open('tests/data/user.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/seats.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/tiers.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/booking_confirmed.sql') as f:
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
    """
    Setup:
      Users:
        - User 1 (u-11111111-...), "Test User"
        - User 2 (u-22222222-...), "Second User"

      Events:
        - Summerfest (e-11111111-...), open_field, 9997 available (was 10000, 3 taken)
        - Opera Night (e-22222222-...), seated, 998 available (was 1000, 2 taken)
        - Rock Arena (e-33333333-...), seated, 500 total/available

      Tiers (for Summerfest):
        - General (et-77777777-...), $50, 9997 available (was 10000, 3 taken)

      Pre-existing bookings (all pending):
        #1 (b-10000000-...-001): User 1, Summerfest, 2x General @ $50 = $100
        #2 (b-10000000-...-002): User 1, Opera Night, A1+A2 @ $150 ea = $300
        #3 (b-10000000-...-003): User 2, Summerfest, 1x General @ $50

    Logged in as User 1.
    Cancel booking #1 once (succeeds), then cancel again -> reject with 400.
    """
    with open('tests/data/user.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/seats.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/tiers.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/booking_pending.sql') as f:
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


async def test_booking_cancel_confirmed(
    test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy
):
    """
    Setup:
      Users:
        - User 1 (u-11111111-...), "Test User"
        - User 2 (u-22222222-...), "Second User"

      Events:
        - Summerfest (e-11111111-...), open_field, 10000 total/available
        - Opera Night (e-22222222-...), seated, 1000 available (took 2 -> 998)
        - Rock Arena (e-33333333-...), seated, 500 total/available

      Tiers (for Summerfest):
        - General (et-77777777-...), $50, 9997 available (was 10000, 3 taken)

      Seats (Opera Night):
        - A1 (es-aaaa...), $150, is_available = FALSE  <- taken by booking #2
        - A2 (es-bbbb...), $150, is_available = FALSE  <- taken by booking #2
        - B1 (es-cccc...), $120, is_available = TRUE

      Pre-existing bookings (all confirmed):
        #1 (b-10000000-...-001): User 1, Summerfest, 2x General @ $50 = $100
        #2 (b-10000000-...-002): User 1, Opera Night, A1+A2 @ $150 ea = $300
        #3 (b-10000000-...-003): User 2, Summerfest, 1x General @ $50

    Logged in as User 1.
    Cancel booking #2 (seated - A1 & A2 on Opera Night).
    """
    with open('tests/data/user.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/seats.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/tiers.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/booking_confirmed.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    override_current_user_dummy()  # bypass authorization, logged in as user 1

    # cancel user 1's seated booking (seats A1 + A2)
    booking_id = "b-10000000-0000-0000-0000-000000000002"

    response = test_client.post(f"/bookings/{booking_id}/cancel")
    data = response.json()

    assert response.status_code == 409
    assert "You cannot cancel this booking" in data["detail"]