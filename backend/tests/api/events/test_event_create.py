from fastapi.testclient import TestClient
from psycopg import AsyncConnection


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

