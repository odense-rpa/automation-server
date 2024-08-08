from fastapi.testclient import TestClient
from sqlmodel import Session

import app.database.models as models

from . import session_fixture, client_fixture, generate_basic_data  # noqa: F401


def test_get_processes(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/api/processes/")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["name"] == "Process"
    assert data[0]["description"] == "Process for unittest"
    assert data[0]["deleted"] is False

    response = client.get("/api/processes/?include_deleted=true")
    data = response.json()
    assert len(data) == 2

def test_create_process(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.post(
        "/api/processes/",
        json={
            "name": "Process",
            "description": "New description",
            "workqueue_id": 1,
            "target_type": "python",
            "target_source": "Test url",
            "target_credentials_id": 0,
            "credentials_id": 0

        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Process"
    assert data["description"] == "New description"

def test_get_process(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/api/processes/1")

    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Process"
    assert data["description"] == "Process for unittest"
    assert data["deleted"] is False

    response = client.get("/api/processes/2")

    assert response.status_code == 403

def test_update_process(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.put(
        "/api/processes/1",
        json={
            "name": "Process",
            "description": "New description",
            "workqueue_id": 1,
            "target_type": "python",
            "target_source": "Test url",
            "target_credentials_id": 1,
            "credentials_id": 1
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Process"
    assert data["description"] == "New description"

    data = session.get(models.Process, 1)

    assert data.name == "Process"
    assert data.description == "New description"
    assert data.workqueue_id == 1
    assert data.target_type == "python"
    assert data.target_source == "Test url"
    assert data.target_credentials_id == 1
    assert data.credentials_id == 1

def test_delete_process(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.delete("/api/processes/1")

    assert response.status_code == 200

    process = session.get(models.Process, 1)
    assert process.deleted is True

    response = client.get("/api/processes/1")
    assert response.status_code == 403

