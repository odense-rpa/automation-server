from fastapi.testclient import TestClient
from sqlmodel import Session

import app.database.models as models


from . import session_fixture, client_fixture, generate_basic_data   # noqa: F401
from app.enums import WorkItemStatus


def test_get_workitem(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/workitems/1")
    data = response.json()

    assert response.status_code == 200

    assert data["reference"] == "Embedded workitem"
    assert data["locked"] is False
    assert data["status"] == WorkItemStatus.NEW

def test_update_workitem(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.put(
        "/workitems/1",
        json={
            "reference": "New reference",
            "data": "{ 'test': 'data' }",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["reference"] == "New reference"
    assert data["data"] == "{ 'test': 'data' }"

def test_update_item_status(session: Session, client: TestClient):
    generate_basic_data(session)

    # Get next item from the workqueue
    response = client.get(
        "/workqueues/1/next_item",
    )
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == WorkItemStatus.IN_PROGRESS
    assert data["locked"] is True

    # Update the item status
    response = client.put(
        f"/workitems/{data['id']}/status",
        json={
            "status": WorkItemStatus.COMPLETED,
        },
    )

    assert response.status_code == 200

    workitem = session.get(models.WorkItem, data["id"])

    assert workitem.status == WorkItemStatus.COMPLETED
    assert workitem.locked is False
    assert workitem.updated_at is not None
    

