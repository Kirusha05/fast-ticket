from fastapi.testclient import TestClient
from psycopg import AsyncConnection
import json


async def test_booking_create_open_field(test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy):
    # event_id: str
    # seat_ids: list[str] | None = None
    # ticket_count: int | None = None

    # Insert test data
    with open('tests/data/user.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    override_current_user_dummy()  # bypass authorizarion
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
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


async def test_booking_create_seated(test_client: TestClient, db_session: AsyncConnection, override_current_user_dummy):
    # event_id: str
    # seat_ids: list[str] | None = None
    # ticket_count: int | None = None

    # Insert test data
    with open('tests/data/user.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    override_current_user_dummy()  # bypass authorizarion
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
    assert data["created_at"] is not None
    assert data["updated_at"] is not None