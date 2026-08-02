from fastapi.testclient import TestClient
from psycopg import AsyncConnection
import json
from unittest.mock import patch, AsyncMock, MagicMock
import pytest

@pytest.mark.asyncio
@patch("usecases.bookings.stripe_client")
async def test_booking_create_tiered(
    mock_stripe_client, test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy
):
    """
    Setup:
      Users:
        - User 1 (u-11111111-...), "Test User"

      Events:
        - Summerfest (e-11111111-...), tiered, 10000 total/available
        - Opera Night (e-22222222-...), seated, 1000 total/available
        - Rock Arena (e-33333333-...), seated, 500 total/available

      Tiers (for Summerfest):
        - General (et-77777777-...), $50, 10000 total/available

    Logged in as User 1.
    Book 2x General tickets on Summerfest -> booking created with 2 tiered_tickets at $50 ea = $100.
    Event and tier available_tickets decremented from 10000 -> 9998.
    """
    with open('tests/data/user.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/tiers.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    fake_session = MagicMock()
    fake_session.id = "cs_test_123"
    fake_session.url = "https://checkout.stripe.com/c/pay/cs_test_123"

    mock_stripe_client.v1.checkout.sessions.create_async = AsyncMock(
        return_value=fake_session
    )

    override_current_user_dummy()  # bypass authorization
    event_id = "e-11111111-1111-1111-1111-111111111111"
    tier_id = "et-77777777-7777-7777-7777-777777777777"

    request = {
        "event_id": event_id,
        "tiered_tickets": [
            {"tier_id": tier_id, "count": 2}
        ]
    }

    response = test_client.post("/bookings", json=request)
    data = response.json()
    # print(json.dumps(data, indent=2))

    assert response.status_code == 201
    assert data["id"] is not None
    assert data["event"]["id"] == event_id
    assert data["status"] == "pending"
    assert data["ticket_count"] == 2
    assert data["total_price"] == 100.0
    assert len(data["seated_tickets"]) == 0
    assert len(data["tiered_tickets"]) == 2
    for tt in data["tiered_tickets"]:
        assert tt["unit_price"] == 50.0
        assert tt["tier_id"] == tier_id
    assert data["created_at"] is not None
    assert data["updated_at"] is not None

    # event available_tickets was decremented (denormalized counter)
    cursor = await db_session.execute(
        "SELECT available_tickets FROM events WHERE id = %s",
        (event_id.removeprefix('e-'),)
    )
    row = await cursor.fetchone()
    assert row['available_tickets'] == 9998

    # tier available_tickets was decremented (authoritative counter)
    cursor = await db_session.execute(
        "SELECT available_tickets FROM event_tiers WHERE id = %s",
        ("77777777-7777-7777-7777-777777777777",)
    )
    row = await cursor.fetchone()
    assert row['available_tickets'] == 9998


@pytest.mark.asyncio
@patch("usecases.bookings.stripe_client")
async def test_booking_create_seated(
    mock_stripe_client, test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy
):
    """
    Setup:
      Users:
        - User 1 (u-11111111-...), "Test User"

      Events:
        - Summerfest (e-11111111-...), tiered, 10000 total/available
        - Opera Night (e-22222222-...), seated, 1000 total/available
        - Rock Arena (e-33333333-...), seated, 500 total/available

      Seats (Opera Night):
        - A1 (es-aaaa...), $150, available
        - A2 (es-bbbb...), $150, available
        - B1 (es-cccc...), $120, available

    Logged in as User 1.
    Book seats A1 + A2 on Opera Night -> booking with 2 seated_tickets @ $150 ea = $300.
    Seats marked unavailable. Event available_tickets decremented from 1000 -> 998.
    """
    with open('tests/data/user.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/seats.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    fake_session = MagicMock()
    fake_session.id = "cs_test_123"
    fake_session.url = "https://checkout.stripe.com/c/pay/cs_test_123"

    mock_stripe_client.v1.checkout.sessions.create_async = AsyncMock(
        return_value=fake_session
    )

    override_current_user_dummy()  # bypass authorization
    event_id = "e-22222222-2222-2222-2222-222222222222"
    seat_ids = [
        "es-aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "es-bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    ]

    request = {
        "event_id": event_id,
        "seat_ids": seat_ids
    }

    response = test_client.post("/bookings", json=request)
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 201
    assert data["id"] is not None
    assert data["event"]["id"] == event_id
    assert data["status"] == "pending"
    assert data["ticket_count"] == 2
    assert data["total_price"] == 300.0
    assert len(data["seated_tickets"]) == 2
    assert data["created_at"] is not None
    assert data["updated_at"] is not None

    # the two booked seats are returned on the booking
    booked = {s["seat_number"] for s in data["seated_tickets"]}
    assert booked == {"A1", "A2"}

    # and persisted as unavailable in the DB
    cursor = await db_session.execute(
        "SELECT seat_number, is_available FROM event_seats "
        "WHERE id = ANY(%s) ORDER BY seat_number",
        ([seat_id.removeprefix("es-") for seat_id in seat_ids],)
    )
    rows = await cursor.fetchall()
    assert [r["seat_number"] for r in rows] == ["A1", "A2"]
    assert all(r["is_available"] is False for r in rows)

    cursor = await db_session.execute(
        "SELECT available_tickets FROM events WHERE id = %s",
        (event_id.removeprefix('e-'),)
    )
    row = await cursor.fetchone()
    assert row['available_tickets'] == 998


async def test_booking_create_seated_wrong_event_seats(
    test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy
):
    """
    Setup:
      Users:
        - User 1 (u-11111111-...), "Test User"

      Events:
        - Summerfest (e-11111111-...), tiered, 10000 total/available
        - Opera Night (e-22222222-...), seated, 1000 total/available
        - Rock Arena (e-33333333-...), seated, 500 total/available

      Seats (Opera Night):
        - A1 (es-aaaa...), $150, available
        - A2 (es-bbbb...), $150, available
        - B1 (es-cccc...), $120, available
      Seats (Rock Arena):
        - A1 (es-dddd...), $200, available
        - A2 (es-eeee...), $200, available
        - A3 (es-ffff...), $200, available

    Logged in as User 1.
    Request booking on Opera Night but pass Rock Arena seats -> reject with 400.
    """
    with open('tests/data/user.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/seats.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    override_current_user_dummy()  # bypass authorization

    # Request booking on Opera Night, but pass seats that belong to Rock Arena
    event_id = "e-22222222-2222-2222-2222-222222222222"
    seat_ids = [
        "es-dddddddd-dddd-dddd-dddd-dddddddddddd",  # Rock Arena, A1
        "es-eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",  # Rock Arena, A2
    ]

    request = {
        "event_id": event_id,
        "seat_ids": seat_ids
    }

    response = test_client.post("/bookings", json=request)
    data = response.json()

    assert response.status_code == 400
    assert "does not belong to event" in data["detail"]


async def test_booking_create_seated_nonexistent_seats(
    test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy
):
    """
    Setup:
      Users:
        - User 1 (u-11111111-...), "Test User"

      Events:
        - Summerfest (e-11111111-...), tiered, 10000 total/available
        - Opera Night (e-22222222-...), seated, 1000 total/available
        - Rock Arena (e-33333333-...), seated, 500 total/available

      Seats (Opera Night):
        - A1 (es-aaaa...), $150, available
        - A2 (es-bbbb...), $150, available
        - B1 (es-cccc...), $120, available

    Logged in as User 1.
    Request booking on Opera Night with one real seat (A1) and one nonexistent seat UUID -> reject with 404.
    """
    with open('tests/data/user.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/seats.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    override_current_user_dummy()  # bypass authorization

    # Request booking with one real seat and one nonexistent seat ID
    event_id = "e-22222222-2222-2222-2222-222222222222"
    seat_ids = [
        "es-aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",  # exists on Opera Night
        "es-00000000-0000-0000-0000-000000000000",  # does not exist
    ]

    request = {
        "event_id": event_id,
        "seat_ids": seat_ids
    }

    response = test_client.post("/bookings", json=request)
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 404
    assert "Seats not found" in data["detail"]


async def test_booking_create_seated_seat_already_taken(
    test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy
):
    """
    Setup:
      Users:
        - User 1 (u-11111111-...), "Test User"
        - User 2 (u-22222222-...), "Second User"

      Events:
        - Summerfest (e-11111111-...), tiered, 9997 available (was 10000, 3 taken)
        - Opera Night (e-22222222-...), seated, 998 available (was 1000, 2 taken)
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
    Try to book A2 (already taken) + B1 (free) -> reject with 409, listing the taken seat A2.
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

    override_current_user_dummy()  # bypass authorization

    # Try to book seat A2 (already taken by the pre-loaded booking) and B1 (still free)
    event_id = "e-22222222-2222-2222-2222-222222222222"
    seat_ids = [
        "es-bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",  # A2 — already taken
        "es-cccccccc-cccc-cccc-cccc-cccccccccccc",  # B1 — still free
    ]

    request = {
        "event_id": event_id,
        "seat_ids": seat_ids
    }

    response = test_client.post("/bookings", json=request)
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 409
    assert data["detail"] == "One or more seats are already taken: A2"


async def test_booking_create_tiered_zero_tickets(
    test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy
):
    """
    Setup:
      Users:
        - User 1 (u-11111111-...), "Test User"

      Events:
        - Summerfest (e-11111111-...), tiered, 10000 total/available
        - Opera Night (e-22222222-...), seated, 1000 total/available
        - Rock Arena (e-33333333-...), seated, 500 total/available

      Tiers (for Summerfest):
        - General (et-77777777-...), $50, 10000 total/available

    Logged in as User 1.
    Request booking with count=0 -> reject with 422 (Pydantic model_validator).
    """
    with open('tests/data/user.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/tiers.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    override_current_user_dummy()  # bypass authorization
    event_id = "e-11111111-1111-1111-1111-111111111111"
    tier_id = "et-77777777-7777-7777-7777-777777777777"

    request = {
        "event_id": event_id,
        "tiered_tickets": [
            {"tier_id": tier_id, "count": 0}
        ]
    }

    response = test_client.post("/bookings", json=request)
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 422
    assert "Ticket count must be at least 1" in str(data["detail"])


@pytest.mark.asyncio
@patch("usecases.bookings.stripe_client")
async def test_booking_create_request_includes_both_tiered_and_seated(
    mock_stripe_client, test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy
):
    """
    Setup:
      Users:
        - User 1 (u-11111111-...), "Test User"

      Events:
        - Summerfest (e-11111111-...), tiered, 10000 total/available
        - Opera Night (e-22222222-...), seated, 1000 total/available
        - Rock Arena (e-33333333-...), seated, 500 total/available

      Tiers (for Summerfest):
        - General (et-77777777-...), $50, 10000 total/available

    Logged in as User 1.
    Book 2x General tickets on Summerfest -> booking created with 2 tiered_tickets at $50 ea = $100.
    Event and tier available_tickets decremented from 10000 -> 9998.
    """
    with open('tests/data/user.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/tiers.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    fake_session = MagicMock()
    fake_session.id = "cs_test_123"
    fake_session.url = "https://checkout.stripe.com/c/pay/cs_test_123"

    mock_stripe_client.v1.checkout.sessions.create_async = AsyncMock(
        return_value=fake_session
    )

    override_current_user_dummy()  # bypass authorization
    event_id = "e-11111111-1111-1111-1111-111111111111"
    tier_id = "et-77777777-7777-7777-7777-777777777777"

    request = {
    "event_id": event_id,
        "tiered_tickets": [
            {"tier_id": tier_id, "count": 2}
        ],
        "seat_ids": [
            "es-aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "es-bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
        ]
    }

    response = test_client.post("/bookings", json=request)
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 422
    assert "Must provide only one of seat_ids or tiered_tickets" in str(data["detail"])


@pytest.mark.asyncio
@patch("usecases.bookings.stripe_client")
async def test_booking_create_tiered_no_tickets_left(
    mock_stripe_client, test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy
):
    """
    Setup:
      Users:
        - User 1 (u-11111111-...), "Test User"

      Events:
        - Summerfest (e-11111111-...), tiered, 10000 total/available
        - Opera Night (e-22222222-...), seated, 1000 total/available
        - Rock Arena (e-33333333-...), seated, 500 total/available

      Tiers (for Summerfest):
        - General (et-77777777-...), $50, 10000 total/available

    Logged in as User 1.
    Book 2x General tickets on Summerfest -> booking created with 2 tiered_tickets at $50 ea = $100.
    Event and tier available_tickets decremented from 10000 -> 9998.
    """
    with open('tests/data/user.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/tiers.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    fake_session = MagicMock()
    fake_session.id = "cs_test_123"
    fake_session.url = "https://checkout.stripe.com/c/pay/cs_test_123"

    mock_stripe_client.v1.checkout.sessions.create_async = AsyncMock(
        return_value=fake_session
    )

    override_current_user_dummy()  # bypass authorization
    event_id = "e-44444444-4444-4444-4444-444444444444"
    tier_id = "et-88888888-8888-8888-8888-888888888888"

    request = {
        "event_id": event_id,
        "tiered_tickets": [
            {"tier_id": tier_id, "count": 2}
        ]
    }

    response = test_client.post("/bookings", json=request)
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 409
    assert data["detail"] == "Not enough tickets available for tier General. Requested: 2, Available: 0"



@pytest.mark.asyncio
@patch("usecases.bookings.stripe_client")
async def test_booking_create_tiered_non_existing_tier(
    mock_stripe_client, test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy
):
    """
    Setup:
      Users:
        - User 1 (u-11111111-...), "Test User"

      Events:
        - Summerfest (e-11111111-...), tiered, 10000 total/available
        - Opera Night (e-22222222-...), seated, 1000 total/available
        - Rock Arena (e-33333333-...), seated, 500 total/available

      Tiers (for Summerfest):
        - General (et-77777777-...), $50, 10000 total/available

    Logged in as User 1.
    Book 2x General tickets on Summerfest -> booking created with 2 tiered_tickets at $50 ea = $100.
    Event and tier available_tickets decremented from 10000 -> 9998.
    """
    with open('tests/data/user.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/tiers.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    fake_session = MagicMock()
    fake_session.id = "cs_test_123"
    fake_session.url = "https://checkout.stripe.com/c/pay/cs_test_123"

    mock_stripe_client.v1.checkout.sessions.create_async = AsyncMock(
        return_value=fake_session
    )

    override_current_user_dummy()  # bypass authorization
    event_id = "e-11111111-1111-1111-1111-111111111111"
    tier_id = "et-77777777-7777-7777-7777-888888888888"

    request = {
        "event_id": event_id,
        "tiered_tickets": [
            {"tier_id": tier_id, "count": 2}
        ]
    }

    response = test_client.post("/bookings", json=request)
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 404
    assert data["detail"] == f"Tiers not found: {tier_id}"


@pytest.mark.asyncio
@patch("usecases.bookings.stripe_client")
async def test_booking_create_tiered_tier_not_belonging_to_event(
    mock_stripe_client, test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy
):
    """
    Setup:
      Users:
        - User 1 (u-11111111-...), "Test User"

      Events:
        - Summerfest (e-11111111-...), tiered, 10000 total/available
        - Opera Night (e-22222222-...), seated, 1000 total/available
        - Rock Arena (e-33333333-...), seated, 500 total/available

      Tiers (for Summerfest):
        - General (et-77777777-...), $50, 10000 total/available

    Logged in as User 1.
    Book 2x General tickets on Summerfest -> booking created with 2 tiered_tickets at $50 ea = $100.
    Event and tier available_tickets decremented from 10000 -> 9998.
    """
    with open('tests/data/user.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/tiers.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    fake_session = MagicMock()
    fake_session.id = "cs_test_123"
    fake_session.url = "https://checkout.stripe.com/c/pay/cs_test_123"

    mock_stripe_client.v1.checkout.sessions.create_async = AsyncMock(
        return_value=fake_session
    )

    override_current_user_dummy()  # bypass authorization
    event_id = "e-11111111-1111-1111-1111-111111111111"
    tier_id = "et-88888888-8888-8888-8888-888888888888"

    request = {
        "event_id": event_id,
        "tiered_tickets": [
            {"tier_id": tier_id, "count": 2}
        ]
    }

    response = test_client.post("/bookings", json=request)
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 400
    assert data["detail"] == f"Tier {tier_id} does not belong to event {event_id}"
