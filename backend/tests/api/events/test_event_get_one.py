from fastapi.testclient import TestClient
from psycopg import AsyncConnection
import json

async def test_events_get_one(test_client: TestClient, db_session: AsyncConnection):
    """
    Setup:
      - Summerfest, open_field, 10000 available
      - Opera Night, seated, 1000 available
      - Rock Arena, seated, 500 available
    """
    with open('tests/data/event.sql') as f:
        await db_session.execute(f.read())
    with open('tests/data/tiers.sql') as f:
        await db_session.execute(f.read())
        await db_session.commit()

    response = test_client.get("/events/e-11111111-1111-1111-1111-111111111111")
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 200

    assert data["name"] == "Summerfest"
    assert data["description"] == "Cel mai tare festival al verii"
    assert data["venue"] == "Gradina Botanica"
    assert data["event_type"] == "open_field"
    assert data["total_tickets"] == 10000
    assert data["available_tickets"] == 10000
    assert len(data["seats"]) == 0
    assert len(data["tiers"]) == 1
    assert data["created_at"] is not None
    assert data["updated_at"] is not None