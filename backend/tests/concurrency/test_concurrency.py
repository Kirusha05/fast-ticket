from psycopg import AsyncConnection
from unittest.mock import patch, AsyncMock, MagicMock
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from main import app
import uuid
import time


@pytest.mark.asyncio
@patch("usecases.bookings.stripe_client")
async def test_booking_create_seated(
    mock_stripe_client, db_session: AsyncConnection, override_current_user_dummy
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

    async def create_booking(barrier: asyncio.Barrier):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://does_not_matter") as client:
            await barrier.wait()  # release all at once
            return await client.post("/bookings", json=request)

    num_requests = 1000
    barrier = asyncio.Barrier(num_requests)
    start = time.perf_counter()
    responses = await asyncio.gather(*(create_booking(barrier) for _ in range(num_requests)))
    elapsed = time.perf_counter() - start
    print(f"Overall RPS: {num_requests / elapsed:.1f}")  # ≈1570 RPS on local machine

    # for r in responses:
        # print(r.status_code)
        # print(r.json())

    successful = [
        r for r in responses
        if r.status_code == 201
    ]

    failed = [
        r for r in responses
        if r.status_code == 409 and "One or more seats are already taken: A1, A2" in str(r.json())
    ]

    assert all(r.status_code in (201, 409) for r in responses)
    assert len(successful) == 1
    assert len(failed) == num_requests - 1

    # verify that only one booking was created
    cursor = await db_session.execute(
        "SELECT COUNT(*) FROM bookings"
    )
    result = await cursor.fetchone()
    assert result['count'] == 1

    # also check the total event tickets
    cursor = await db_session.execute(
        "SELECT available_tickets FROM events WHERE id = %s",
        (event_id.removeprefix('e-'),)
    )
    row = await cursor.fetchone()
    assert row['available_tickets'] == 998
    

@pytest.mark.asyncio
@patch("usecases.bookings.stripe_client")
async def test_booking_create_tiered(
    mock_stripe_client, db_session: AsyncConnection, override_current_user_dummy
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

    def make_fake_session(*args, **kwargs):
        session = MagicMock()
        session.id = f"cs_test_{uuid.uuid4().hex}"
        session.url = f"https://checkout.stripe.com/c/pay/{session.id}"
        return session

    mock_stripe_client.v1.checkout.sessions.create_async = AsyncMock(
        side_effect=make_fake_session
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

    async def create_booking(barrier: asyncio.Barrier):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://does_not_matter") as client:
            await barrier.wait()  # release all at once
            return await client.post("/bookings", json=request)

    num_requests = 6000
    barrier = asyncio.Barrier(num_requests)

    start = time.perf_counter()
    responses = await asyncio.gather(*(create_booking(barrier) for _ in range(num_requests)))
    elapsed = time.perf_counter() - start
    print(f"Overall RPS: {num_requests / elapsed:.1f}")  # 400 RPS on local machine
    # the General tier is a hot row that gets locked by each request
    # to be noted that this is the worst‑case scenario (all requests for the same event/tier at the exact same instant)
    # in a real app, traffic would be spread across different events and time -> less contention -> higher real RPS

    successful = [
        r for r in responses
        if r.status_code == 201
    ]

    failed = [
        r for r in responses
        if r.status_code == 409 and "Not enough tickets available for tier General" in str(r.json())
    ]

    assert all(r.status_code in (201, 409) for r in responses)
    assert len(successful) == 5000  # 5000 bookings x 2 tickets each = 10000 total available tickets for the event
    assert len(failed) == 1000  # other 1000 should fail

    # verify that exactly 5000 bookings were created
    cursor = await db_session.execute(
        "SELECT COUNT(*) FROM bookings"
    )
    result = await cursor.fetchone()
    assert result['count'] == 5000

    # also check the total event tickets
    cursor = await db_session.execute(
        "SELECT available_tickets FROM events WHERE id = %s",
        (event_id.removeprefix('e-'),)
    )
    row = await cursor.fetchone()
    assert row['available_tickets'] == 0

    # and the tier available_tickets
    cursor = await db_session.execute(
        "SELECT available_tickets FROM event_tiers WHERE id = %s",
        (tier_id.removeprefix('et-'),)
    )
    row = await cursor.fetchone()
    assert row['available_tickets'] == 0