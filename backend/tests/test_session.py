from fastapi.testclient import TestClient
from sqlmodel import Session

import app.enums as enums

from . import session_fixture, client_fixture, generate_basic_data  # noqa: F401

def test_get_sessions(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/api/sessions/")
    data = response.json()

    assert response.status_code == 200
    assert len(data["items"]) == 3

    item = data["items"][2]

    assert item["id"] == 1
    assert item["process_id"] == 1
    assert item["resource_id"] is None
    assert item["deleted"] is False
    assert item["status"] == enums.SessionStatus.NEW

    response = client.get("/api/sessions/?include_deleted=true")
    data = response.json()
    assert len(data["items"]) == 4

def test_get_session(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/api/sessions/1")

    data = response.json()

    assert response.status_code == 200
    assert data["process_id"] == 1
    assert data["resource_id"] is None
    assert data["status"] == enums.SessionStatus.NEW
    assert data["dispatched_at"] is None

def test_update_status_fail(session: Session, client: TestClient):
    generate_basic_data(session)

    # Change status to IN_PROGRESS without assigning a resource
    response = client.put(
        "/api/sessions/1/status",
        json={
            "status": enums.SessionStatus.IN_PROGRESS,
        },
    )
    assert response.status_code == 400
    assert response.json()['detail'] == "Resource must be assigned to update status"

    # Change status to FAILED from NEW which is invalid
    response = client.put(
        "/api/sessions/1/status",
        json={
            "status": enums.SessionStatus.FAILED,
        },
    )
    assert response.status_code == 400
    assert response.json()['detail'] == "Invalid status transition"

    # Attempt to change status of a non-existent session
    response = client.put(
        "/api/sessions/5/status",
        json={
            "status": enums.SessionStatus.IN_PROGRESS,
        },
    )
    assert response.status_code == 404

def test_get_new_sessions(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/api/sessions/new")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["process_id"] == 1
    assert data[0]["resource_id"] is None
    assert data[0]["status"] == enums.SessionStatus.NEW


def test_session_reset_on_resource_detach(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/api/sessions/4")
    data = response.json()

    assert data["resource_id"] is not None
    assert data["status"] == enums.SessionStatus.NEW
    assert data["dispatched_at"] is not None

    # Now trigger a detach on the resource
    response = client.get("/api/resources")
    assert response.status_code == 200

    response = client.get("/api/sessions/4")
    data = response.json()

    assert data["resource_id"] is None
    assert data["status"] == enums.SessionStatus.NEW
    assert data["dispatched_at"] is None

def test_create_session(session: Session, client: TestClient):
    generate_basic_data(session)

    # Check if a process exists
    response = client.get("/api/processes/1")
    assert response.status_code == 200

    response = client.post(
        "/api/sessions/",
        json={
            "process_id": 1,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["process_id"] == 1
    #assert data["resource_id"] == 1
    assert data["status"] == enums.SessionStatus.NEW