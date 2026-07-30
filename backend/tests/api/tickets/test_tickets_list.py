from fastapi.testclient import TestClient
from psycopg import AsyncConnection
import json


async def test_tickets_list_tiered(test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy):
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

      Pre-existing bookings (all confirmed):
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
    with open('tests/data/booking_confirmed.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/tickets.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    override_current_user_dummy()  # bypass authorization, logged in as user 1

    booking_id = "b-10000000-0000-0000-0000-000000000001"  # tiered / tiered

    response = test_client.get(f"/tickets/{booking_id}")
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 200
    assert len(data) == 2
    assert all(ticket['tier_id'] is not None for ticket in data)
    assert all(ticket['seat_id'] is None for ticket in data)


async def test_tickets_list_seated(test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy):
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

      Pre-existing bookings (all confirmed):
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
    with open('tests/data/booking_confirmed.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/tickets.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    override_current_user_dummy()  # bypass authorization, logged in as user 1

    booking_id = "b-10000000-0000-0000-0000-000000000002"  # seated

    response = test_client.get(f"/tickets/{booking_id}")
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 200
    assert len(data) == 2
    assert all(ticket['tier_id'] is None for ticket in data)
    assert all(ticket['seat_id'] is not None for ticket in data)