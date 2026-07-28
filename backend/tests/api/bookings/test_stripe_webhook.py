from fastapi.testclient import TestClient
from psycopg import AsyncConnection
import json
from unittest.mock import patch, MagicMock
import pytest


@pytest.mark.asyncio
@patch("routes.webhooks.stripe")
async def test_stripe_booking_completed_webhook_open_field(
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

    # user 1's open-field booking (2x General)
    booking_id = "b-10000000-0000-0000-0000-000000000001"
    stripe_checkout_session_id = "cs_test_10000000000000000000000001"
    stripe_payment_intent_id = "pi_test_10000000000000000000000001"

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
    assert row['status'] == 'confirmed'
    assert not row['expires_at']

    # check the updated payment row
    cursor = await db_session.execute(
        "SELECT * FROM payments WHERE stripe_checkout_session_id = %s",
        (stripe_checkout_session_id,)
    )
    row = await cursor.fetchone()
    assert str(row['booking_id']) == booking_id.lstrip("b-")
    assert row['status'] == 'succeeded'
    assert row['stripe_payment_intent_id'] == stripe_payment_intent_id

    # check the created tickets rows
    cursor = await db_session.execute(
        "SELECT * FROM tickets WHERE booking_id = %s",
        (booking_id.lstrip("b-"),)
    )
    rows = await cursor.fetchall()
    assert len(rows) == 2
    assert all([str(r["booking_id"]) == booking_id.lstrip("b-") for r in rows])
    assert all([str(r["event_id"]) == "11111111-1111-1111-1111-111111111111" for r in rows])
    assert all([r["seat_id"] is None for r in rows])
    assert all([r["tier_id"] is not None for r in rows])


@pytest.mark.asyncio
@patch("routes.webhooks.stripe")
async def test_stripe_booking_completed_webhook_seated(
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
    assert row['status'] == 'confirmed'
    assert not row['expires_at']

    # check the updated payment row
    cursor = await db_session.execute(
        "SELECT * FROM payments WHERE stripe_checkout_session_id = %s",
        (stripe_checkout_session_id,)
    )
    row = await cursor.fetchone()
    assert str(row['booking_id']) == booking_id.lstrip("b-")
    assert row['status'] == 'succeeded'
    assert row['stripe_payment_intent_id'] == stripe_payment_intent_id

    # check the created tickets rows
    cursor = await db_session.execute(
        "SELECT * FROM tickets WHERE booking_id = %s",
        (booking_id.lstrip("b-"),)
    )
    rows = await cursor.fetchall()
    assert len(rows) == 2
    assert all([str(r["booking_id"]) == booking_id.lstrip("b-") for r in rows])
    assert all([str(r["event_id"]) == "22222222-2222-2222-2222-222222222222" for r in rows])
    assert all([r["seat_id"] is not None for r in rows])
    assert all([r["tier_id"] is None for r in rows])


@pytest.mark.asyncio
@patch("routes.webhooks.stripe")
async def test_stripe_booking_expired_webhook(
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
