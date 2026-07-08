from datetime import datetime, timedelta

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, update

from app.database.models import AuditLog, WorkItem, Workqueue
from app.database.repository import WorkqueueRepository
from app.enums import WorkItemStatus
from app.services import WorkqueueService

from . import generate_basic_data  # noqa: F401


async def test_get_workqueues_information(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/workqueues/information")
    assert response.status_code == 200

    data = response.json()
    # Only non-deleted workqueue should appear
    assert len(data) == 1

    queue = data[0]
    assert queue["name"] == "Workqueue"
    assert queue["enabled"] is True
    assert queue["new"] == 1
    assert queue["in_progress"] == 1
    assert queue["completed"] == 1
    assert queue["failed"] == 1
    assert queue["pending_user_action"] == 1

    # With include_deleted, both queues should appear
    response = await client.get("/workqueues/information?include_deleted=true")
    data = response.json()
    assert len(data) == 2

    # Deleted queue should have zero counts
    deleted_queue = next(q for q in data if q["name"] == "Deleted workqueue")
    assert deleted_queue["new"] == 0
    assert deleted_queue["in_progress"] == 0
    assert deleted_queue["completed"] == 0
    assert deleted_queue["failed"] == 0
    assert deleted_queue["pending_user_action"] == 0


async def test_get_workqueues(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/workqueues/")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["name"] == "Workqueue"
    assert data[0]["description"] == "Queue for unittest"
    assert data[0]["enabled"] is True
    assert data[0]["deleted"] is False

    response = await client.get("/workqueues/?include_deleted=true")
    data = response.json()
    assert len(data) == 2


async def test_get_workqueue(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/workqueues/1")

    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Workqueue"
    assert data["description"] == "Queue for unittest"
    assert data["enabled"] is True
    assert data["deleted"] is False


async def test_update_workqueue(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.put(
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

    data = await session.get(Workqueue, 1)

    assert data.name == "Workqueue"
    assert data.description == "New description"


async def test_create_workqueue(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.post(
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

    data = await session.get(Workqueue, 3)

    assert data.name == "New workqueue"
    assert data.description == "New description"
    assert data.enabled is False
    assert data.created_at is not None
    assert data.updated_at is not None


async def test_add_workitem(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.post(
        "/workqueues/1/add",
        json={"data": {}, "reference": "My reference"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["data"] == {}
    assert data["reference"] == "My reference"
    assert data["status"] == WorkItemStatus.NEW
    assert data["locked"] is False

    data = await session.get(WorkItem, 2)

    assert data.data == {}
    assert data.reference == "Embedded workitem"
    assert data.status == WorkItemStatus.IN_PROGRESS
    assert data.locked is False


async def test_next_item(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/workqueues/1/next_item")

    assert response.status_code == 200

    data = response.json()
    assert data["data"] == {}
    assert data["reference"] == "Embedded workitem"
    assert data["status"] == WorkItemStatus.IN_PROGRESS
    assert data["locked"] is True

    data = await session.get(WorkItem, 1)

    assert data.data == {}
    assert data.reference == "Embedded workitem"
    assert data.status == WorkItemStatus.IN_PROGRESS
    assert data.locked is True

    response = await client.get("/workqueues/1/next_item")

    assert response.status_code == 204


async def test_next_item_disabled_queue(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.put(
        "/workqueues/1",
        json={
            "name": "Workqueue",
            "description": "New description",
            "enabled": False,
        },
    )
    assert response.status_code == 200

    response = await client.get("/workqueues/1/next_item")

    assert response.status_code == 204


async def test_clear_queue_dates(session: AsyncSession, client: AsyncClient):
    # test clear queue with id 1 workitem days older than 1
    # assert zero removals
    # test clear queue with id 1 workitem days older than 0
    # assert removals

    await generate_basic_data(session)

    response = await client.post("/workqueues/1/clear", json={"days_older_than": 1})
    assert response.status_code == 204

    response = await client.get("/workqueues/1/items")
    data = response.json()
    assert data["total_items"] == 5

    response = await client.post("/workqueues/1/clear", json={"days_older_than": 0})
    assert response.status_code == 204

    response = await client.get("/workqueues/1/items")
    data = response.json()
    assert data["total_items"] == 0


async def test_clear_queue_all_parameters(session: AsyncSession, client: AsyncClient):
    # test clear queue with id 1 all parameters
    # assert removals and non removals

    await generate_basic_data(session)

    response = await client.post(
        "/workqueues/1/clear", json={"workitem_status": "new", "days_older_than": 0}
    )
    assert response.status_code == 204

    response = await client.get("/workqueues/1/items")
    data = response.json()
    assert data["total_items"] == 4

    response = await client.post(
        "/workqueues/1/clear", json={"workitem_status": "failed", "days_older_than": 0}
    )
    assert response.status_code == 204

    response = await client.get("/workqueues/1/items")
    data = response.json()
    assert data["total_items"] == 3

    response = await client.post(
        "/workqueues/1/clear",
        json={"workitem_status": "completed", "days_older_than": 1},
    )
    assert response.status_code == 204

    response = await client.get("/workqueues/1/items")
    data = response.json()
    assert data["total_items"] == 3


async def test_clear_queue_no_parameters(session: AsyncSession, client: AsyncClient):
    # test clear queue with id 1 no parameters
    # assert queue is empty

    await generate_basic_data(session)

    response = await client.post("/workqueues/1/clear", json={})
    assert response.status_code == 204

    response = await client.get("/workqueues/1/items")
    data = response.json()
    assert data["total_items"] == 0


async def test_workitems_paging(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/workqueues/1/items?page=1&size=2")
    assert response.status_code == 200

    data = response.json()
    assert data["total_items"] == 5
    assert len(data["items"]) == 2
    assert data["total_pages"] == 3


async def test_workitems_paging_with_search(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/workqueues/1/items?page=1&size=2&search=emBed")
    assert response.status_code == 200

    data = response.json()
    assert data["total_items"] == 5


async def test_get_workitems_by_reference_in_workqueue(
    session: AsyncSession, client: AsyncClient
):
    await generate_basic_data(session)

    # Test getting items by reference within a specific workqueue
    response = await client.get("/workqueues/1/by_reference/Embedded workitem")
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
    response = await client.get("/workqueues/1/by_reference/NonExistentReference")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 0


async def test_get_workqueue_by_name(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/workqueues/by_name/Workqueue")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Workqueue"


async def test_get_workqueue_by_name_with_spaces(
    session: AsyncSession, client: AsyncClient
):
    await generate_basic_data(session)

    # Create a workqueue with spaces in the name
    response = await client.post(
        "/workqueues/",
        json={
            "name": "Client library test",
            "description": "Test queue",
            "enabled": True,
        },
    )
    assert response.status_code == 200

    # Look it up by name — %20 spaces must be decoded correctly
    response = await client.get("/workqueues/by_name/Client library test")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Client library test"


async def test_get_workitems_by_reference_in_workqueue_with_status_filter(
    session: AsyncSession, client: AsyncClient
):
    await generate_basic_data(session)

    # Test filtering by COMPLETED status within workqueue
    response = await client.get(
        "/workqueues/1/by_reference/Embedded workitem?status=completed"
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1  # Only one COMPLETED item in workqueue 1
    assert data[0]["status"] == WorkItemStatus.COMPLETED
    assert data[0]["reference"] == "Embedded workitem"
    assert data[0]["workqueue_id"] == 1

    # Test filtering by NEW status within workqueue
    response = await client.get(
        "/workqueues/1/by_reference/Embedded workitem?status=new"
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1  # Only one NEW item in workqueue 1
    assert data[0]["status"] == WorkItemStatus.NEW
    assert data[0]["reference"] == "Embedded workitem"
    assert data[0]["workqueue_id"] == 1

    # Test filtering by status that doesn't exist for this reference in this workqueue
    response = await client.get(
        "/workqueues/1/by_reference/NonExistentReference?status=completed"
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 0


async def test_create_workqueue_with_auto_clean(
    session: AsyncSession, client: AsyncClient
):
    await generate_basic_data(session)

    response = await client.post(
        "/workqueues/",
        json={
            "name": "Auto-clean workqueue",
            "description": "Queue with auto-clean",
            "enabled": True,
            "auto_clean_max_age_days": 30,
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert data["auto_clean_max_age_days"] == 30

    workqueue = await session.get(Workqueue, 3)
    assert workqueue.auto_clean_max_age_days == 30


async def test_update_workqueue_auto_clean(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    # Default is disabled
    response = await client.get("/workqueues/1")
    assert response.json()["auto_clean_max_age_days"] is None

    # Enable auto-clean
    response = await client.put(
        "/workqueues/1",
        json={
            "name": "Workqueue",
            "description": "Queue for unittest",
            "enabled": True,
            "auto_clean_max_age_days": 14,
        },
    )
    assert response.status_code == 200
    assert response.json()["auto_clean_max_age_days"] == 14

    # Disable again
    response = await client.put(
        "/workqueues/1",
        json={
            "name": "Workqueue",
            "description": "Queue for unittest",
            "enabled": True,
            "auto_clean_max_age_days": None,
        },
    )
    assert response.status_code == 200
    assert response.json()["auto_clean_max_age_days"] is None


async def test_workqueue_auto_clean_validation(
    session: AsyncSession, client: AsyncClient
):
    await generate_basic_data(session)

    for invalid_value in (0, -1):
        response = await client.put(
            "/workqueues/1",
            json={
                "name": "Workqueue",
                "description": "Queue for unittest",
                "enabled": True,
                "auto_clean_max_age_days": invalid_value,
            },
        )
        assert response.status_code == 422


async def test_auto_clean_workqueues(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    # Enable auto-clean on workqueue 1 (30 days)
    await session.execute(
        update(Workqueue).where(Workqueue.id == 1).values(auto_clean_max_age_days=30)
    )

    # Backdate all items in the fixture (NEW, IN_PROGRESS, COMPLETED, FAILED,
    # PENDING_USER_ACTION) past the cutoff
    old_date = datetime.now() - timedelta(days=40)
    await session.execute(update(WorkItem).values(updated_at=old_date))

    # Add a fresh COMPLETED item that must survive
    session.add(
        WorkItem(
            status=WorkItemStatus.COMPLETED,
            data={},
            reference="Fresh item",
            locked=False,
            workqueue_id=1,
        )
    )

    # Audit log referencing the old COMPLETED item (id 3)
    session.add(
        AuditLog(
            event_timestamp=datetime.now(),
            session_id=1,
            workitem_id=3,
            message="Log for completed item",
            created_at=datetime.now(),
        )
    )
    await session.commit()

    service = WorkqueueService(WorkqueueRepository(session))
    await service.auto_clean_workqueues()
    session.expire_all()

    # Old COMPLETED (3) and FAILED (4) deleted
    assert await session.get(WorkItem, 3) is None
    assert await session.get(WorkItem, 4) is None

    # Old non-terminal items survive
    assert (await session.get(WorkItem, 1)).status == WorkItemStatus.NEW
    assert (await session.get(WorkItem, 2)).status == WorkItemStatus.IN_PROGRESS
    assert (await session.get(WorkItem, 5)).status == WorkItemStatus.PENDING_USER_ACTION

    # Fresh COMPLETED item survives
    assert (await session.get(WorkItem, 6)).status == WorkItemStatus.COMPLETED

    # Audit log survives with its workitem link severed
    audit_log = (
        await session.scalars(
            select(AuditLog).where(AuditLog.message == "Log for completed item")
        )
    ).first()
    assert audit_log is not None
    assert audit_log.workitem_id is None


async def test_auto_clean_skips_workqueues_without_setting(
    session: AsyncSession, client: AsyncClient
):
    await generate_basic_data(session)

    # No workqueue has auto-clean enabled; backdate everything
    old_date = datetime.now() - timedelta(days=400)
    await session.execute(update(WorkItem).values(updated_at=old_date))
    await session.commit()

    service = WorkqueueService(WorkqueueRepository(session))
    await service.auto_clean_workqueues()
    session.expire_all()

    response = await client.get("/workqueues/1/items")
    assert response.json()["total_items"] == 5
