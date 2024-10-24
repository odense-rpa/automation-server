from fastapi.testclient import TestClient
from sqlmodel import Session

from app.database.models import Workqueue, WorkItem


from . import session_fixture, client_fixture, generate_basic_data  # noqa: F401
from app.enums import WorkItemStatus


def test_get_workqueues(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/api/workqueues/")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["name"] == "Workqueue"
    assert data[0]["description"] == "Queue for unittest"
    assert data[0]["enabled"] is True
    assert data[0]["deleted"] is False

    response = client.get("/api/workqueues/?include_deleted=true")
    data = response.json()
    assert len(data) == 2


def test_get_workqueue(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/api/workqueues/1")

    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Workqueue"
    assert data["description"] == "Queue for unittest"
    assert data["enabled"] is True
    assert data["deleted"] is False


def test_update_workqueue(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.put(
        "/api/workqueues/1",
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
        "/api/workqueues/",
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
        "/api/workqueues/1/add",
        json={"data": "{}", "reference": "My reference"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["data"] == "{}"
    assert data["reference"] == "My reference"
    assert data["status"] == WorkItemStatus.NEW
    assert data["locked"] is False

    data = session.get(WorkItem, 2)

    assert data.data == "{}"
    assert data.reference == "Embedded workitem"
    assert data.status == WorkItemStatus.IN_PROGRESS
    assert data.locked is False


def test_next_item(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/api/workqueues/1/next_item")

    assert response.status_code == 200

    data = response.json()
    assert data["data"] == "{}"
    assert data["reference"] == "Embedded workitem"
    assert data["status"] == WorkItemStatus.IN_PROGRESS
    assert data["locked"] is True

    data = session.get(WorkItem, 1)

    assert data.data == "{}"
    assert data.reference == "Embedded workitem"
    assert data.status == WorkItemStatus.IN_PROGRESS
    assert data.locked is True

    response = client.get("/api/workqueues/1/next_item")

    assert response.status_code == 204

def test_clear_queue_dates(session: Session, client: TestClient):
    # test clear queue with id 1 workitem days older than 1
    # assert zero removals
    # test clear queue with id 1 workitem days older than 0
    # assert removals

    generate_basic_data(session)

    response = client.post(
        "/api/workqueues/1/clear",
        json = {            
            "days_older_than": 1
        }
    )
    assert response.status_code == 204

    response = client.get("/api/workqueues/1/items")
    data = response.json()
    assert data["total_items"] == 5

    response = client.post(
        "/api/workqueues/1/clear",
        json = {            
            "days_older_than": 0
        }
    )
    assert response.status_code == 204

    response = client.get("/api/workqueues/1/items")
    data = response.json()    
    assert data["total_items"] == 0

def test_clear_queue_all_parameters(session: Session, client: TestClient):
    # test clear queue with id 1 all parameters
    # assert removals and non removals

    generate_basic_data(session)

    response = client.post(
        "/api/workqueues/1/clear",
        json = {
            "workitem_status": "new",
            "days_older_than": 0
        }
    )
    assert response.status_code == 204

    response = client.get("/api/workqueues/1/items")
    data = response.json()
    assert data["total_items"] == 4

    response = client.post(
        "/api/workqueues/1/clear",
        json = {
            "workitem_status": "failed",
            "days_older_than": 0
        }
    )
    assert response.status_code == 204

    response = client.get("/api/workqueues/1/items")
    data = response.json()    
    assert data["total_items"] == 3

    response = client.post(
        "/api/workqueues/1/clear",
        json = {
            "workitem_status": "completed",
            "days_older_than": 1
        }
    )
    assert response.status_code == 204

    response = client.get("/api/workqueues/1/items")
    data = response.json()    
    assert data["total_items"] == 3
    

def test_clear_queue_no_parameters(session: Session, client: TestClient):
    # test clear queue with id 1 no parameters
    # assert queue is empty

    generate_basic_data(session)    

    response = client.post(
        "/api/workqueues/1/clear",
        json = {}
    )
    assert response.status_code == 204

    response = client.get("/api/workqueues/1/items")
    data = response.json()
    assert data["total_items"] == 0