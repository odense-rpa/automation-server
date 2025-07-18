from fastapi.testclient import TestClient
from sqlmodel import Session

import app.database.models as models
import app.enums as enums


from . import generate_basic_data  # noqa: F401


def test_get_triggers(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/processes/1/trigger")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 3

    assert data[0]["type"] == enums.TriggerType.CRON

    response = client.get("/processes/1/trigger?include_deleted=true")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 4

def test_create_trigger(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.post(
        "/processes/1/trigger",
        json={
            "type": enums.TriggerType.CRON,
            "cron": "0 0 * * *",
            "enabled": True,
            "parameters": "--queue"
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["id"] == 5
    assert data["type"] == enums.TriggerType.CRON
    assert data["cron"] == "0 0 * * *"
    assert data["parameters"] == "--queue"

def test_create_trigger_failures(session: Session, client: TestClient):
    generate_basic_data(session)

    # Missing cron
    response = client.post(
        "/processes/1/trigger",
        json={
            "type": enums.TriggerType.CRON,
            "cron": "0 ",
            "enabled": True
        },
    )
    assert response.status_code == 422

    # Missing date
    response = client.post(
        "/processes/1/trigger",
        json={
            "type": enums.TriggerType.DATE,
            "date": None,
            "enabled": True
        },
    )
    assert response.status_code == 422

    # Missing workqueue
    response = client.post(
        "/processes/1/trigger",
        json={
            "type": enums.TriggerType.WORKQUEUE,
            "workqueue_id": None,
            "enabled": True
        },
    )
    assert response.status_code == 422

    # Note that other invalid combinations will be removed in the controller

# Test delete trigger
def test_delete_trigger(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.delete("/triggers/1")
    assert response.status_code == 204

    response = client.get("/processes/1/trigger?include_deleted=false")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2

def test_update_trigger(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.put(
        "/triggers/1",
        json={
            "type": enums.TriggerType.CRON,
            "cron": "10 10 * * *",
            "enabled": True
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["id"] == 1
    assert data["type"] == enums.TriggerType.CRON
    assert data["cron"] == "10 10 * * *"

    # Change a cron trigger to a workqueue trigger
    response = client.put(
        "/triggers/1",
        json={
            "type": enums.TriggerType.WORKQUEUE,
            "workqueue_id": 1,
            "enabled": True
        },
    )

    data = response.json()
    assert response.status_code == 200
    assert data["id"] == 1
    assert data["type"] == enums.TriggerType.WORKQUEUE
    assert data["workqueue_id"] == 1
    assert data["cron"] == ""