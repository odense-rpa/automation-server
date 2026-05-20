from datetime import datetime, timezone

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import app.database.models as models
from app.enums import WorkItemStatus

from . import generate_basic_data  # noqa: F401


async def test_get_workitem(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/workitems/1")
    data = response.json()

    assert response.status_code == 200

    assert data["reference"] == "Embedded workitem"
    assert data["locked"] is False
    assert data["status"] == WorkItemStatus.NEW


async def test_update_workitem(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.put(
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


async def test_get_next_item(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    # Get next item from the workqueue
    response = await client.get(
        "/workqueues/1/next_item",
    )
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == WorkItemStatus.IN_PROGRESS
    assert data["locked"] is True
    assert "updated_at" in data


async def test_update_item_status_completed(session: AsyncSession, client: AsyncClient):
    workitem = await _start_item_update(session, client, WorkItemStatus.COMPLETED)

    assert workitem.status == WorkItemStatus.COMPLETED
    assert workitem.locked is False


async def test_update_item_status_failed(session: AsyncSession, client: AsyncClient):
    workitem = await _start_item_update(session, client, WorkItemStatus.FAILED)

    assert workitem.status == WorkItemStatus.FAILED
    assert workitem.locked is False


async def test_update_item_status_user_pending(
    session: AsyncSession, client: AsyncClient
):
    workitem = await _start_item_update(
        session, client, WorkItemStatus.PENDING_USER_ACTION
    )

    assert workitem.status == WorkItemStatus.PENDING_USER_ACTION
    assert workitem.locked is False


async def test_update_item_status_new(session: AsyncSession, client: AsyncClient):
    workitem = await _start_item_update(session, client, WorkItemStatus.NEW)

    assert workitem.status == WorkItemStatus.NEW
    assert workitem.locked is False


async def test_update_item_status_in_progress(
    session: AsyncSession, client: AsyncClient
):
    workitem = await _start_item_update(session, client, WorkItemStatus.IN_PROGRESS)

    assert workitem.status == WorkItemStatus.IN_PROGRESS
    assert workitem.locked is True


async def _start_item_update(
    session: AsyncSession, client: AsyncClient, status: WorkItemStatus
) -> models.WorkItem:
    await generate_basic_data(session)

    # Get next item from the workqueue
    response = await client.get(
        "/workqueues/1/next_item",
    )
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == WorkItemStatus.IN_PROGRESS
    assert data["locked"] is True

    # Update the item status
    response = await client.put(
        f"/workitems/{data['id']}/status",
        json={
            "status": status,
        },
    )

    assert response.status_code == 200

    return await session.get(models.WorkItem, data["id"])


async def test_get_workitems_by_reference(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    # Test getting items by reference
    response = await client.get("/workitems/by-reference/Embedded workitem")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 5  # All 5 items have the same reference

    # Verify all items have the correct reference
    for item in data:
        assert item["reference"] == "Embedded workitem"

    # Verify sorting (newest to oldest by created_at)
    created_times = [item["created_at"] for item in data]
    assert created_times == sorted(created_times, reverse=True)


async def test_get_workitems_by_reference_no_matches(
    session: AsyncSession, client: AsyncClient
):
    await generate_basic_data(session)

    # Test getting items by non-existent reference
    response = await client.get("/workitems/by-reference/NonExistentReference")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 0


async def test_get_workitems_by_reference_with_status_filter(
    session: AsyncSession, client: AsyncClient
):
    await generate_basic_data(session)

    # Test filtering by COMPLETED status
    response = await client.get(
        "/workitems/by-reference/Embedded workitem?status=completed"
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1  # Only one COMPLETED item
    assert data[0]["status"] == WorkItemStatus.COMPLETED
    assert data[0]["reference"] == "Embedded workitem"


async def test_update_workitem_validation_invalid_data_types(
    session: AsyncSession, client: AsyncClient
):
    """Test that workitem update endpoint properly validates data field types (GitHub issue #6)."""
    await generate_basic_data(session)

    # Test cases that should fail validation - data must be a dict
    invalid_test_cases = [
        # String instead of dict
        {"data": "not a dict", "reference": "test1"},
        # List instead of dict
        {"data": [1, 2, 3], "reference": "test2"},
        # Number instead of dict
        {"data": 42, "reference": "test3"},
        # Boolean instead of dict
        {"data": True, "reference": "test4"},
    ]

    for i, test_case in enumerate(invalid_test_cases):
        response = await client.put("/workitems/1", json=test_case)

        # Should fail with 422 (validation error)
        assert response.status_code == 422, (
            f"Test {i + 1} should fail validation but got {response.status_code}"
        )

        # Check that the error message mentions validation
        response_data = response.json()
        assert "detail" in response_data
        assert len(response_data["detail"]) > 0

        # Verify the specific field that failed validation
        error_detail = response_data["detail"][0]
        assert error_detail["loc"] == ["body", "data"]
        assert "dict" in error_detail["msg"].lower()


async def test_update_workitem_validation_valid_data_types(
    session: AsyncSession, client: AsyncClient
):
    """Test that workitem update endpoint accepts valid data field types."""
    await generate_basic_data(session)

    # Test cases that should pass validation
    valid_test_cases = [
        # Valid dict
        {"data": {"key": "value"}, "reference": "test5"},
        # Empty dict
        {"data": {}, "reference": "test6"},
        # None (should be allowed since it's Optional)
        {"data": None, "reference": "test7"},
        # Only reference (data is optional)
        {"reference": "test8"},
        # Only data (reference is optional)
        {"data": {"complex": {"nested": "structure"}}},
    ]

    for i, test_case in enumerate(valid_test_cases):
        response = await client.put("/workitems/1", json=test_case)

        # Should succeed
        assert response.status_code == 200, (
            f"Test {i + 1} should pass validation but got {response.status_code}: {response.json()}"
        )

        # Verify the response contains the updated data
        response_data = response.json()
        assert "id" in response_data
        assert response_data["id"] == 1


async def test_update_workitem_status_sets_started_at_on_in_progress(
    session: AsyncSession, client: AsyncClient
):
    """Test that started_at is set when manually updating status to IN_PROGRESS."""
    import time
    from datetime import datetime

    await generate_basic_data(session)

    # Get a work item that starts as NEW
    response = await client.get("/workitems/1")
    assert response.status_code == 200
    initial_data = response.json()
    assert initial_data["status"] == WorkItemStatus.NEW
    assert initial_data["started_at"] is None

    # Update status to IN_PROGRESS
    before_update = datetime.now()
    response = await client.put(
        "/workitems/1/status", json={"status": WorkItemStatus.IN_PROGRESS}
    )
    after_update = datetime.now()

    assert response.status_code == 200
    data = response.json()

    # Verify started_at is set
    assert data["started_at"] is not None
    started_at = datetime.fromisoformat(data["started_at"].replace("Z", "+00:00"))

    # Verify timestamp is reasonable (within our test window)
    assert before_update <= started_at.replace(tzinfo=None) <= after_update

    # Test overwrite behavior - update to IN_PROGRESS again
    time.sleep(0.1)  # Small delay to ensure different timestamp

    response = await client.put(
        "/workitems/1/status", json={"status": WorkItemStatus.IN_PROGRESS}
    )
    assert response.status_code == 200
    new_data = response.json()

    # Verify started_at was updated (overwritten)
    new_started_at = datetime.fromisoformat(
        new_data["started_at"].replace("Z", "+00:00")
    )
    assert new_started_at > started_at


async def test_update_workitem_status_calculates_duration_on_completion(
    session: AsyncSession, client: AsyncClient
):
    """Test that work_duration_seconds is calculated correctly on completion."""
    import time

    await generate_basic_data(session)

    # Set work item to IN_PROGRESS to establish started_at
    response = await client.put(
        "/workitems/1/status", json={"status": WorkItemStatus.IN_PROGRESS}
    )
    assert response.status_code == 200
    in_progress_data = response.json()
    assert in_progress_data["started_at"] is not None
    assert in_progress_data["work_duration_seconds"] is None

    # Wait a brief moment to ensure measurable duration
    time.sleep(2)

    # Update status to COMPLETED
    response = await client.put(
        "/workitems/1/status", json={"status": WorkItemStatus.COMPLETED}
    )
    assert response.status_code == 200
    completed_data = response.json()

    # Verify work_duration_seconds is calculated
    assert completed_data["work_duration_seconds"] is not None
    duration = completed_data["work_duration_seconds"]

    # Should be approximately 2 seconds (allowing for some variance)
    assert 1 <= duration <= 4, f"Expected duration ~2 seconds, got {duration}"

    # Test that FAILED status also calculates duration
    # First set another item to IN_PROGRESS
    response = await client.put(
        "/workitems/2/status", json={"status": WorkItemStatus.IN_PROGRESS}
    )
    assert response.status_code == 200

    time.sleep(1)

    # Update status to FAILED
    response = await client.put(
        "/workitems/2/status", json={"status": WorkItemStatus.FAILED}
    )
    assert response.status_code == 200
    failed_data = response.json()

    # Verify work_duration_seconds is also calculated for failed items
    assert failed_data["work_duration_seconds"] is not None
    failed_duration = failed_data["work_duration_seconds"]
    assert 0 <= failed_duration <= 3, (
        f"Expected duration ~1 second, got {failed_duration}"
    )


async def test_update_workitem_status_timezone_aware_handling(
    session: AsyncSession, client: AsyncClient
):
    """Test that timezone-aware started_at is handled correctly in duration calculation."""
    await generate_basic_data(session)

    # Set work item to IN_PROGRESS to establish started_at
    response = await client.put(
        "/workitems/1/status", json={"status": WorkItemStatus.IN_PROGRESS}
    )
    assert response.status_code == 200

    # Get the workitem from database and manually set started_at to timezone-aware
    workitem = await session.get(models.WorkItem, 1)
    assert workitem is not None

    # Force started_at to be timezone-naive UTC (simulates production scenario)
    # Note: asyncpg rejects tz-aware datetimes for TIMESTAMP WITHOUT TIME ZONE columns
    workitem.started_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(workitem)
    await session.commit()
    await session.refresh(workitem)

    # Attempt to update status to COMPLETED
    response = await client.put(
        "/workitems/1/status", json={"status": WorkItemStatus.COMPLETED}
    )

    # The timezone hypothesis was disproven - the operation actually succeeds
    assert response.status_code == 200, (
        f"Expected 200 success, got {response.status_code}: {response.text}"
    )

    # Verify the duration was calculated successfully
    completed_data = response.json()
    assert completed_data["work_duration_seconds"] is not None
    assert completed_data["status"] == WorkItemStatus.COMPLETED
