from fastapi.testclient import TestClient
from psycopg import AsyncConnection
import json


async def test_booking_get_own(
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

      Seats (Opera Night):
        - A1 (es-aaaa...), $150, is_available = FALSE  <- taken by booking #2
        - A2 (es-bbbb...), $150, is_available = FALSE  <- taken by booking #2
        - B1 (es-cccc...), $120, is_available = TRUE

      Pre-existing bookings (all confirmed):
        #1 (b-10000000-...-001): User 1, Summerfest, 2x General @ $50 = $100
        #2 (b-10000000-...-002): User 1, Opera Night, A1+A2 @ $150 ea = $300
        #3 (b-10000000-...-003): User 2, Summerfest, 1x General @ $50

    Logged in as User 1.
    Fetch booking #2 (own seated booking) -> return full details with seated_tickets and total_price.
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

    # fetch user 1's seated booking (seats A1 + A2)
    booking_id = "b-10000000-0000-0000-0000-000000000002"

    response = test_client.get(f"/bookings/{booking_id}")
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 200
    assert data["id"] == booking_id
    assert data["event"]["id"] == "e-22222222-2222-2222-2222-222222222222"
    assert data["status"] == "confirmed"
    assert data["ticket_count"] == 2
    assert data["total_price"] == 300.0
    assert len(data["seated_tickets"]) == 2


async def test_booking_get_not_own(
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

      Pre-existing bookings (all confirmed):
        #1 (b-10000000-...-001): User 1, Summerfest, 2x General @ $50 = $100
        #2 (b-10000000-...-002): User 1, Opera Night, A1+A2 @ $150 ea = $300
        #3 (b-10000000-...-003): User 2, Summerfest, 1x General @ $50

    Logged in as User 1.
    Try to fetch booking #3 (belongs to User 2) -> reject with 403.
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

    # try to fetch user 2's booking
    booking_id = "b-10000000-0000-0000-0000-000000000003"

    response = test_client.get(f"/bookings/{booking_id}")
    data = response.json()

    assert response.status_code == 403
    assert data["detail"] == "You are not allowed to view this booking"