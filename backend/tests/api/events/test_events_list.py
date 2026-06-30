from fastapi.testclient import TestClient
from psycopg import AsyncConnection
import json


def test_events_list_empty(test_client: TestClient, db_session: AsyncConnection):
    """
    Setup: empty database
    """
    response = test_client.get("/events")
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 200
    assert data == []


async def test_events_list_all_no_bookings(test_client: TestClient, db_session: AsyncConnection):
    """
    Setup:
      - Summerfest, open_field, 10000 available
      - Opera Night, seated, 1000 available
      - Rock Arena, seated, 500 available
    """
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    response = test_client.get("/events")
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 200
    assert len(data) == 3

    # Verify all expected IDs are present
    returned_ids = {e["id"] for e in data}
    assert returned_ids == {
        "e-11111111-1111-1111-1111-111111111111",
        "e-22222222-2222-2222-2222-222222222222",
        "e-33333333-3333-3333-3333-333333333333",
    }

    # Build a dict by event id for easier assertions
    by_id = {e["id"]: e for e in data}

    summerfest = by_id["e-11111111-1111-1111-1111-111111111111"]
    assert summerfest["name"] == "Summerfest"
    assert summerfest["description"] == "Cel mai tare festival al verii"
    assert summerfest["venue"] == "Gradina Botanica"
    assert summerfest["event_type"] == "open_field"
    assert summerfest["total_tickets"] == 10000
    assert summerfest["available_tickets"] == 10000
    assert summerfest["seats"] == []
    assert summerfest["tiers"] == []
    assert summerfest["created_at"] is not None
    assert summerfest["updated_at"] is not None

    opera = by_id["e-22222222-2222-2222-2222-222222222222"]
    assert opera["name"] == "Opera Night"
    assert opera["description"] == "O seara de opera clasica"
    assert opera["venue"] == "Ateneul Roman"
    assert opera["event_type"] == "seated"
    assert opera["total_tickets"] == 1000
    assert opera["available_tickets"] == 1000
    assert opera["seats"] == []
    assert opera["tiers"] == []

    rock = by_id["e-33333333-3333-3333-3333-333333333333"]
    assert rock["name"] == "Rock Arena"
    assert rock["description"] == "Concert rock cu trupe internationale"
    assert rock["venue"] == "Sala Palatului"
    assert rock["event_type"] == "seated"
    assert rock["total_tickets"] == 500
    assert rock["available_tickets"] == 500
    assert rock["seats"] == []
    assert rock["tiers"] == []


async def test_events_list_after_bookings(
    test_client: TestClient, db_session: AsyncConnection
):
    """
    Setup: full dataset with pre-existing bookings:
      - Summerfest: 10000 total, 9997 available (3 tickets booked)
      - Opera Night: 1000 total, 998 available (2 seats booked)
      - Rock Arena: 500 total, 500 available (no bookings)
    """
    with open('tests/data/user.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/tiers.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/seats.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/booking.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    response = test_client.get("/events")
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 200
    assert len(data) == 3

    by_id = {e["id"]: e for e in data}

    # Summerfest: 3 of 10000 tickets taken
    summerfest = by_id["e-11111111-1111-1111-1111-111111111111"]
    assert summerfest["total_tickets"] == 10000
    assert summerfest["available_tickets"] == 9997

    # Opera Night: 2 of 1000 seats taken
    opera = by_id["e-22222222-2222-2222-2222-222222222222"]
    assert opera["total_tickets"] == 1000
    assert opera["available_tickets"] == 998

    # Rock Arena: untouched
    rock = by_id["e-33333333-3333-3333-3333-333333333333"]
    assert rock["total_tickets"] == 500
    assert rock["available_tickets"] == 500


async def test_events_list_filter_open_field(
    test_client: TestClient, db_session: AsyncConnection
):
    """
    Setup: all 3 events loaded (Summerfest open_field, Opera Night seated, Rock Arena seated).
    GET /events?event_type=open_field -> only Summerfest returned.
    """
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    response = test_client.get("/events?event_type=open_field")
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 200
    assert len(data) == 1

    event = data[0]
    assert event["id"] == "e-11111111-1111-1111-1111-111111111111"
    assert event["name"] == "Summerfest"
    assert event["event_type"] == "open_field"


async def test_events_list_filter_seated(
    test_client: TestClient, db_session: AsyncConnection
):
    """
    Setup: all 3 events loaded.
    GET /events?event_type=seated -> Opera Night and Rock Arena returned.
    """
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    response = test_client.get("/events?event_type=seated")
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 200
    assert len(data) == 2

    returned_ids = {e["id"] for e in data}
    assert returned_ids == {
        "e-22222222-2222-2222-2222-222222222222",
        "e-33333333-3333-3333-3333-333333333333",
    }
    assert all(e["event_type"] == "seated" for e in data)


def test_events_list_filter_invalid(
    test_client: TestClient, db_session: AsyncConnection
):
    """
    GET /events?event_type=bogus -> 422 validation error
    because "bogus" is not a valid EventType.
    """
    response = test_client.get("/events?event_type=bogus")
    assert response.status_code == 422