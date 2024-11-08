from fastapi.testclient import TestClient
from sqlmodel import Session

from . import session_fixture, client_fixture, generate_basic_data  # noqa: F401


def test_get_empty_sessionlogs(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/api/sessionlogs/4?page=1&size=10")
    data = response.json()

    assert response.status_code == 200
    assert data["page"] == 1
    assert data["total_items"] == 0
    assert data["total_pages"] == 0
    assert len(data["items"]) == 0


def test_get_nonexistant_session(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/api/sessionlogs/220202?page=1&size=10")
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "Session not found"

def test_get_deleted_session(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/api/sessionlogs/2?page=1&size=10")
    assert response.status_code == 410

def test_search_sessionlogs(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/api/sessionlogs/3?page=1&size=1")
    data = response.json()

    assert response.status_code == 200
    assert data["page"] == 1
    assert data["total_items"] == 3
    assert data["total_pages"] == 3
    assert len(data["items"]) == 1

    response = client.get("/api/sessionlogs/3?page=1&size=1&search=nothing")
    data = response.json()

    assert response.status_code == 200
    assert data["page"] == 1
    assert data["total_items"] == 1
    assert data["total_pages"] == 1
    assert len(data["items"]) == 1
