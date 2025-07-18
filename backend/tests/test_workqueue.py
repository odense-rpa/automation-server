from fastapi.testclient import TestClient
from sqlmodel import Session

from app.database.models import Workqueue, WorkItem


from . import generate_basic_data  # noqa: F401
from app.enums import WorkItemStatus


def test_get_workqueues(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/workqueues/")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["name"] == "Workqueue"
    assert data[0]["description"] == "Queue for unittest"
    assert data[0]["enabled"] is True
    assert data[0]["deleted"] is False

    response = client.get("/workqueues/?include_deleted=true")
    data = response.json()
    assert len(data) == 2


def test_get_workqueue(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/workqueues/1")

    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Workqueue"
    assert data["description"] == "Queue for unittest"
    assert data["enabled"] is True
    assert data["deleted"] is False


def test_update_workqueue(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.put(
        "/workqueues/1",
        json={
            "name": "Workqueue",
            "description": "New description",
            "enabled": True,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Workqueue"
    assert data["description"] == "New description"
    assert data["enabled"] is True
    assert data["deleted"] is False

    data = session.get(Workqueue, 1)

    assert data.name == "Workqueue"
    assert data.description == "New description"


def test_create_workqueue(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.post(
        "/workqueues/",
        json={
            "name": "New workqueue",
            "description": "New description",
            "enabled": False,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "New workqueue"
    assert data["description"] == "New description"
    assert data["enabled"] is False
    assert data["deleted"] is False

    data = session.get(Workqueue, 3)

    assert data.name == "New workqueue"
    assert data.description == "New description"
    assert data.enabled is False
    assert data.created_at is not None
    assert data.updated_at is not None


def test_add_workitem(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.post(
        "/workqueues/1/add",
        json={"data": {}, "reference": "My reference"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["data"] == {}
    assert data["reference"] == "My reference"
    assert data["status"] == WorkItemStatus.NEW
    assert data["locked"] is False

    data = session.get(WorkItem, 2)

    assert data.data == {}
    assert data.reference == "Embedded workitem"
    assert data.status == WorkItemStatus.IN_PROGRESS
    assert data.locked is False


def test_next_item(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/workqueues/1/next_item")

    assert response.status_code == 200

    data = response.json()
    assert data["data"] == {}
    assert data["reference"] == "Embedded workitem"
    assert data["status"] == WorkItemStatus.IN_PROGRESS
    assert data["locked"] is True

    data = session.get(WorkItem, 1)

    assert data.data == {}
    assert data.reference == "Embedded workitem"
    assert data.status == WorkItemStatus.IN_PROGRESS
    assert data.locked is True

    response = client.get("/workqueues/1/next_item")

    assert response.status_code == 204

def test_next_item_disabled_queue(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.put(
        "/workqueues/1",
        json={
            "name": "Workqueue",
            "description": "New description",
            "enabled": False,
        },
    )
    assert response.status_code == 200


    response = client.get("/workqueues/1/next_item")

    assert response.status_code == 204



def test_clear_queue_dates(session: Session, client: TestClient):
    # test clear queue with id 1 workitem days older than 1
    # assert zero removals
    # test clear queue with id 1 workitem days older than 0
    # assert removals

    generate_basic_data(session)

    response = client.post(
        "/workqueues/1/clear",
        json = {            
            "days_older_than": 1
        }
    )
    assert response.status_code == 204

    response = client.get("/workqueues/1/items")
    data = response.json()
    assert data["total_items"] == 5

    response = client.post(
        "/workqueues/1/clear",
        json = {            
            "days_older_than": 0
        }
    )
    assert response.status_code == 204

    response = client.get("/workqueues/1/items")
    data = response.json()    
    assert data["total_items"] == 0

def test_clear_queue_all_parameters(session: Session, client: TestClient):
    # test clear queue with id 1 all parameters
    # assert removals and non removals

    generate_basic_data(session)

    response = client.post(
        "/workqueues/1/clear",
        json = {
            "workitem_status": "new",
            "days_older_than": 0
        }
    )
    assert response.status_code == 204

    response = client.get("/workqueues/1/items")
    data = response.json()
    assert data["total_items"] == 4

    response = client.post(
        "/workqueues/1/clear",
        json = {
            "workitem_status": "failed",
            "days_older_than": 0
        }
    )
    assert response.status_code == 204

    response = client.get("/workqueues/1/items")
    data = response.json()    
    assert data["total_items"] == 3

    response = client.post(
        "/workqueues/1/clear",
        json = {
            "workitem_status": "completed",
            "days_older_than": 1
        }
    )
    assert response.status_code == 204

    response = client.get("/workqueues/1/items")
    data = response.json()    
    assert data["total_items"] == 3
    

def test_clear_queue_no_parameters(session: Session, client: TestClient):
    # test clear queue with id 1 no parameters
    # assert queue is empty

    generate_basic_data(session)    

    response = client.post(
        "/workqueues/1/clear",
        json = {}
    )
    assert response.status_code == 204

    response = client.get("/workqueues/1/items")
    data = response.json()
    assert data["total_items"] == 0


def test_workitems_paging(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/workqueues/1/items?page=1&size=2")
    assert response.status_code == 200

    data = response.json()
    assert data["total_items"] == 5
    assert len(data["items"]) == 2
    assert data["total_pages"] == 3


def test_workitems_paging_with_search(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/workqueues/1/items?page=1&size=2&search=emBed")
    assert response.status_code == 200

    data = response.json()
    assert data["total_items"] == 5


def test_get_workitems_by_reference_in_workqueue(session: Session, client: TestClient):
    generate_basic_data(session)

    # Test getting items by reference within a specific workqueue
    response = client.get("/workqueues/1/by_reference/Embedded workitem")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 5  # All 5 items have the same reference and are in workqueue 1
    
    # Verify all items have the correct reference and workqueue
    for item in data:
        assert item["reference"] == "Embedded workitem"
        assert item["workqueue_id"] == 1
    
    # Verify sorting (newest to oldest by created_at)
    created_times = [item["created_at"] for item in data]
    assert created_times == sorted(created_times, reverse=True)

    # Test with non-existent reference
    response = client.get("/workqueues/1/by_reference/NonExistentReference")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 0


def test_get_workitems_by_reference_in_workqueue_with_status_filter(session: Session, client: TestClient):
    generate_basic_data(session)

    # Test filtering by COMPLETED status within workqueue
    response = client.get("/workqueues/1/by_reference/Embedded workitem?status=completed")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1  # Only one COMPLETED item in workqueue 1
    assert data[0]["status"] == WorkItemStatus.COMPLETED
    assert data[0]["reference"] == "Embedded workitem"
    assert data[0]["workqueue_id"] == 1

    # Test filtering by NEW status within workqueue
    response = client.get("/workqueues/1/by_reference/Embedded workitem?status=new")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1  # Only one NEW item in workqueue 1
    assert data[0]["status"] == WorkItemStatus.NEW
    assert data[0]["reference"] == "Embedded workitem"
    assert data[0]["workqueue_id"] == 1

    # Test filtering by status that doesn't exist for this reference in this workqueue
    response = client.get("/workqueues/1/by_reference/NonExistentReference?status=completed")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 0
