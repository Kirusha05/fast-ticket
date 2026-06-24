from fastapi.testclient import TestClient
from psycopg import AsyncConnection
import json


def test_event_create_with_tickets(test_client: TestClient, db_session: AsyncConnection):
    request = {
        "name": "Summerfest",
        "description": "Cel mai tare festival al verii",
        "venue": "Gradina Botanica",
        "event_date": "2026-06-21",
        "event_type": "open_field",
        "total_tickets": 10000
    }

    response = test_client.post("/events/", json=request)
    data = response.json()

    assert response.status_code == 201
    assert data["id"] is not None
    assert data["name"] == request["name"]
    assert data["description"] == request["description"]
    assert data["venue"] == request["venue"]
    assert data["event_date"] is not None
    assert data["total_tickets"] == request["total_tickets"]
    assert data["available_tickets"] == request["total_tickets"]
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


async def test_event_create_with_seats(test_client: TestClient, db_session: AsyncConnection):
    request = {
        "name": "Opera Night",
        "description": "O seara de opera clasica",
        "venue": "Ateneul Roman",
        "event_date": "2026-06-21",
        "event_type": "seated",
        "seats": [
            {"seat_number": "A1", "price": 150.0},
            {"seat_number": "A2", "price": 150.0},
            {"seat_number": "B1", "price": 120.0}
        ]
    }

    response = test_client.post("/events/", json=request)
    data = response.json()
    print(json.dumps(data, indent=2))

    assert response.status_code == 201
    assert data["id"] is not None
    assert data["name"] == request["name"]
    assert data["event_type"] == "seated"
    assert data["total_tickets"] == 3

    event_id = data["id"]

    # verify all seats were inserted and tied to the created event
    cursor = await db_session.execute(
        "SELECT seat_number, price FROM seats WHERE event_id = %s ORDER BY seat_number",
        (event_id.removeprefix("e-"),)
    )
    rows = await cursor.fetchall()
    assert len(rows) == 3
    assert [r["seat_number"] for r in rows] == ["A1", "A2", "B1"]
    assert [r["price"] for r in rows] == [150.0, 150.0, 120.0]


def test_event_create_without_tickets(test_client: TestClient, db_session: AsyncConnection):
    request = {
        "name": "Summerfest",
        "description": "Cel mai tare festival al verii",
        "venue": "Gradina Botanica",
        "event_date": "2026-06-21",
        "event_type": "open_field"
    }

    response = test_client.post("/events/", json=request)
    data = response.json()

    assert response.status_code == 201
    assert data["id"] is not None
    assert data["name"] == request["name"]
    assert data["description"] == request["description"]
    assert data["venue"] == request["venue"]
    assert data["event_date"] is not None
    assert not data["total_tickets"]
    assert not data["available_tickets"]
    assert data["created_at"] is not None
    assert data["updated_at"] is not None
