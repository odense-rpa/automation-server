from fastapi.testclient import TestClient
from sqlmodel import Session

import app.database.models as models


from . import generate_basic_data  # noqa: F401
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
            "data": {"test": "data"},
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["reference"] == "New reference"
    assert data["data"] == {"test": "data"}


def test_get_next_item(session: Session, client: TestClient):
    generate_basic_data(session)

    # Get next item from the workqueue
    response = client.get(
        "/workqueues/1/next_item",
    )
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == WorkItemStatus.IN_PROGRESS
    assert data["locked"] is True
    assert "updated_at" in data


def test_update_item_status_completed(session: Session, client: TestClient):
    workitem = _start_item_update(session, client, WorkItemStatus.COMPLETED)

    assert workitem.status == WorkItemStatus.COMPLETED
    assert workitem.locked is False


def test_update_item_status_failed(session: Session, client: TestClient):
    workitem = _start_item_update(session, client, WorkItemStatus.FAILED)

    assert workitem.status == WorkItemStatus.FAILED
    assert workitem.locked is False


def test_update_item_status_user_pending(session: Session, client: TestClient):
    workitem = _start_item_update(session, client, WorkItemStatus.PENDING_USER_ACTION)

    assert workitem.status == WorkItemStatus.PENDING_USER_ACTION
    assert workitem.locked is False


def test_update_item_status_new(session: Session, client: TestClient):
    workitem = _start_item_update(session, client, WorkItemStatus.NEW)

    assert workitem.status == WorkItemStatus.NEW
    assert workitem.locked is False


def test_update_item_status_in_progress(session: Session, client: TestClient):
    workitem = _start_item_update(session, client, WorkItemStatus.IN_PROGRESS)

    assert workitem.status == WorkItemStatus.IN_PROGRESS
    assert workitem.locked is True


def _start_item_update(
    session: Session, client: TestClient, status: WorkItemStatus
) -> models.WorkItem:
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
            "status": status,
        },
    )

    assert response.status_code == 200

    return session.get(models.WorkItem, data["id"])


def test_get_workitems_by_reference(session: Session, client: TestClient):
    generate_basic_data(session)

    # Test getting items by reference
    response = client.get("/workitems/by-reference/Embedded workitem")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 5  # All 5 items have the same reference
    
    # Verify all items have the correct reference
    for item in data:
        assert item["reference"] == "Embedded workitem"
    
    # Verify sorting (newest to oldest by created_at)
    created_times = [item["created_at"] for item in data]
    assert created_times == sorted(created_times, reverse=True)


def test_get_workitems_by_reference_no_matches(session: Session, client: TestClient):
    generate_basic_data(session)

    # Test getting items by non-existent reference
    response = client.get("/workitems/by-reference/NonExistentReference")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 0


def test_get_workitems_by_reference_with_status_filter(session: Session, client: TestClient):
    generate_basic_data(session)

    # Test filtering by COMPLETED status
    response = client.get("/workitems/by-reference/Embedded workitem?status=completed")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1  # Only one COMPLETED item
    assert data[0]["status"] == WorkItemStatus.COMPLETED
    assert data[0]["reference"] == "Embedded workitem"


