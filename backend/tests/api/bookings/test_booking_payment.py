from fastapi.testclient import TestClient
from psycopg import AsyncConnection
import json
from unittest.mock import patch, AsyncMock, MagicMock
import pytest


@pytest.mark.asyncio
@patch("usecases.bookings.stripe_client")
async def test_booking_create_checkout_session(
    mock_stripe_client, test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy
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
    List all bookings for User 1 -> should return only #1 and #2 (2 bookings).
    """
    with open('tests/data/user.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/tiers.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/seats.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/booking_pending.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    fake_session = MagicMock()
    fake_session.id = "cs_test_123"
    fake_session.url = "https://checkout.stripe.com/c/pay/cs_test_123"

    mock_stripe_client.v1.checkout.sessions.create_async = AsyncMock(
        return_value=fake_session
    )

    override_current_user_dummy()  # bypass authorization, logged in as user 1

    # user 1's seated booking (seats A1 + A2)
    booking_id = "b-10000000-0000-0000-0000-000000000002"

    response = test_client.post(f"/bookings/{booking_id}/payment")
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 201
    mock_stripe_client.v1.checkout.sessions.create_async.assert_awaited_once()

    # check the created payment row
    cursor = await db_session.execute(
        "SELECT * FROM payments WHERE stripe_checkout_session_id = %s",
        ("cs_test_123",)
    )
    row = await cursor.fetchone()
    print(row)
    assert str(row['booking_id']) == booking_id.lstrip("b-")
    assert row['status'] == 'pending'
    assert row['amount_cents'] == 30000  # 30000 cents = $300 on the original booking
    assert not row['stripe_payment_intent_id']


@pytest.mark.asyncio
@patch("routes.webhooks.stripe")
async def test_booking_payment_completed_webhook(
    mock_stripe, test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy
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

      Payment:
          p-10000000-0000-0000-0000-000000000002, booking_id b-10000000-...-002, pending, cs_test_10000000000000000000000002

    Logged in as User 1.
    List all bookings for User 1 -> should return only #1 and #2 (2 bookings).
    """
    with open('tests/data/scenarios/bookings/stripe_webhook_handler.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    override_current_user_dummy()  # bypass authorization, logged in as user 1

    # user 1's seated booking (seats A1 + A2)
    booking_id = "b-10000000-0000-0000-0000-000000000002"
    stripe_checkout_session_id = "cs_test_10000000000000000000000002"
    stripe_payment_intent_id = "pi_test_10000000000000000000000002"

    fake_session = MagicMock()
    fake_session.type = "checkout.session.completed"  # event type sent by Stripe
    fake_session.data.object = {
        "id": stripe_checkout_session_id,
        "metadata": {
            "booking_id": booking_id
        },
        "payment_intent": stripe_payment_intent_id
    }

    mock_stripe.Webhook.construct_event.return_value = fake_session

    response = test_client.post("/webhooks/stripe")
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 200
    mock_stripe.Webhook.construct_event.assert_called_once()

    # check the updated booking row
    cursor = await db_session.execute(
        "SELECT * FROM bookings WHERE id = %s",
        (booking_id.lstrip("b-"),)
    )
    row = await cursor.fetchone()
    print(row)
    assert row['status'] == 'confirmed'
    assert row['stripe_checkout_session_id'] == stripe_checkout_session_id
    assert row['stripe_payment_intent_id'] == stripe_payment_intent_id
    assert not row['expires_at']

    # check the updated payment row
    cursor = await db_session.execute(
        "SELECT * FROM payments WHERE stripe_checkout_session_id = %s",
        (stripe_checkout_session_id,)
    )
    row = await cursor.fetchone()
    print(row)
    assert str(row['booking_id']) == booking_id.lstrip("b-")
    assert row['status'] == 'succeeded'
    assert row['stripe_payment_intent_id'] == stripe_payment_intent_id


@pytest.mark.asyncio
@patch("routes.webhooks.stripe")
async def test_booking_payment_expired(
    mock_stripe, test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy
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

      Payment:
          p-10000000-0000-0000-0000-000000000002, booking_id b-10000000-...-002, pending, cs_test_10000000000000000000000002

    Logged in as User 1.
    List all bookings for User 1 -> should return only #1 and #2 (2 bookings).
    """
    with open('tests/data/scenarios/bookings/stripe_webhook_handler.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    override_current_user_dummy()  # bypass authorization, logged in as user 1

    # user 1's seated booking (seats A1 + A2)
    booking_id = "b-10000000-0000-0000-0000-000000000002"
    stripe_checkout_session_id = "cs_test_10000000000000000000000002"
    stripe_payment_intent_id = "pi_test_10000000000000000000000002"

    fake_session = MagicMock()
    fake_session.type = "checkout.session.expired"  # event type sent by Stripe
    fake_session.data.object = {
        "id": stripe_checkout_session_id,
        "metadata": {
            "booking_id": booking_id
        },
        "payment_intent": stripe_payment_intent_id
    }

    mock_stripe.Webhook.construct_event.return_value = fake_session

    response = test_client.post("/webhooks/stripe")
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 200
    mock_stripe.Webhook.construct_event.assert_called_once()

    # check the updated booking row
    cursor = await db_session.execute(
        "SELECT * FROM bookings WHERE id = %s",
        (booking_id.lstrip("b-"),)
    )
    row = await cursor.fetchone()
    print(row)
    assert row['status'] == 'expired'
    assert row['stripe_checkout_session_id'] == stripe_checkout_session_id
    assert not row['stripe_payment_intent_id']
    assert not row['expires_at']

    # check the updated payment row
    cursor = await db_session.execute(
        "SELECT * FROM payments WHERE stripe_checkout_session_id = %s",
        (stripe_checkout_session_id,)
    )
    row = await cursor.fetchone()
    print(row)
    assert str(row['booking_id']) == booking_id.lstrip("b-")
    assert row['status'] == 'expired'
    assert not row['stripe_payment_intent_id']

    # check if the resources (seats here) were released, 
    # copied from test_booking_cancel.test_booking_cancel_seated_status_pending
    
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


@pytest.mark.asyncio
@patch("routes.webhooks.stripe")
async def test_booking_payment_failed(
    mock_stripe, test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy
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

      Payment:
          p-10000000-0000-0000-0000-000000000002, booking_id b-10000000-...-002, pending, cs_test_10000000000000000000000002

    Logged in as User 1.
    List all bookings for User 1 -> should return only #1 and #2 (2 bookings).
    """
    with open('tests/data/scenarios/bookings/stripe_webhook_handler.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    override_current_user_dummy()  # bypass authorization, logged in as user 1

    # user 1's seated booking (seats A1 + A2)
    booking_id = "b-10000000-0000-0000-0000-000000000002"
    stripe_checkout_session_id = "cs_test_10000000000000000000000002"
    stripe_payment_intent_id = "pi_test_10000000000000000000000002"

    fake_session = MagicMock()
    fake_session.type = "payment_intent.payment_failed"  # event type sent by Stripe
    fake_session.data.object = {
        "id": stripe_checkout_session_id,
        "metadata": {
            "booking_id": booking_id
        },
        "payment_intent": stripe_payment_intent_id
    }

    mock_stripe.Webhook.construct_event.return_value = fake_session

    response = test_client.post("/webhooks/stripe")
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 200
    mock_stripe.Webhook.construct_event.assert_called_once()

    # check the updated booking row
    cursor = await db_session.execute(
        "SELECT * FROM bookings WHERE id = %s",
        (booking_id.lstrip("b-"),)
    )
    row = await cursor.fetchone()
    print(row)
    assert row['status'] == 'payment_failed'
    assert row['stripe_checkout_session_id'] == stripe_checkout_session_id
    assert not row['stripe_payment_intent_id']
    assert row['expires_at']

    # check the updated payment row
    cursor = await db_session.execute(
        "SELECT * FROM payments WHERE stripe_checkout_session_id = %s",
        (stripe_checkout_session_id,)
    )
    row = await cursor.fetchone()
    print(row)
    assert str(row['booking_id']) == booking_id.lstrip("b-")
    assert row['status'] == 'failed'
    assert not row['stripe_payment_intent_id']

    # check if the resources (seats here) are still booked, as they should NOT be released 
    # copied from test_booking_cancel.test_booking_cancel_seated_status_pending
    
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
    assert all(r["is_available"] is False for r in rows)

    # the booking_seated_tickets rows for the cancelled booking are gone
    cursor = await db_session.execute(
        "SELECT COUNT(*) AS count FROM booking_seated_tickets WHERE booking_id = %s",
        ("10000000-0000-0000-0000-000000000002",)
    )
    row = await cursor.fetchone()
    assert row["count"] == 2

    # the event's available tickets get increased
    cursor = await db_session.execute(
        "SELECT available_tickets FROM events WHERE id = %s",
        ("22222222-2222-2222-2222-222222222222",)
    )
    row = await cursor.fetchone()
    assert row['available_tickets'] == 998  # were 998 initially and should stay 998