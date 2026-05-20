from datetime import datetime

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from . import generate_basic_data  # noqa: F401


async def test_get_empty_sessionlogs(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/audit-logs/4?page=1&size=10")
    data = response.json()

    assert response.status_code == 200
    assert data["page"] == 1
    assert data["total_items"] == 0
    assert data["total_pages"] == 0
    assert len(data["items"]) == 0


async def test_get_nonexistant_session(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/audit-logs/220202?page=1&size=10")
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "Session not found"


async def test_get_deleted_session(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/audit-logs/2?page=1&size=10")
    assert response.status_code == 410


async def test_search_sessionlogs(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/audit-logs/3?page=1&size=1")
    data = response.json()

    assert response.status_code == 200
    assert data["page"] == 1
    assert data["total_items"] == 3
    assert data["total_pages"] == 3
    assert len(data["items"]) == 1

    response = await client.get("/audit-logs/3?page=1&size=1&search=nOthing")
    data = response.json()

    assert response.status_code == 200
    assert data["page"] == 1
    assert data["total_items"] == 1
    assert data["total_pages"] == 1
    assert len(data["items"]) == 1


async def test_create_audit_log(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    try:
        # Test minimal required fields
        response = await client.post(
            "/audit-logs",
            json={
                "message": "Test log message",
                "event_timestamp": datetime.now().isoformat(),
            },
        )

        if response.status_code != 204:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")

        assert response.status_code == 204

        # Test with session_id
        response = await client.post(
            "/audit-logs",
            json={
                "message": "Test log message with session",
                "session_id": 1,
                "event_timestamp": datetime.now().isoformat(),
            },
        )

        assert response.status_code == 204
    except Exception as e:
        print(f"Exception: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        raise


async def test_create_audit_log_with_all_fields(
    session: AsyncSession, client: AsyncClient
):
    await generate_basic_data(session)

    response = await client.post(
        "/audit-logs",
        json={
            "message": "Detailed log message",
            "session_id": 1,
            "workitem_id": 1,
            "level": "ERROR",
            "logger_name": "test.logger",
            "module": "test_module",
            "function_name": "test_function",
            "line_number": 42,
            "event_timestamp": datetime.now().isoformat(),
            "exception_type": "ValueError",
            "exception_message": "Invalid value",
            "traceback": "Traceback...",
            "structured_data": {
                "http_call": {"method": "POST", "url": "https://api.example.com/test"}
            },
        },
    )

    assert response.status_code == 204


async def test_create_audit_log_validation(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    # Missing required field 'message'
    response = await client.post("/audit-logs", json={"session_id": 1})

    assert response.status_code == 422


async def test_get_by_workitem(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    # WorkItem 1 has one audit log entry (see __init__.py line 241-248)
    response = await client.get("/audit-logs/by_workitem/1")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["workitem_id"] == 1
    assert data[0]["message"] == "Test log 2"


async def test_get_by_workitem_empty(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    # WorkItem 2 has no audit logs
    response = await client.get("/audit-logs/by_workitem/2")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 0


async def test_get_by_workitem_not_found(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/audit-logs/by_workitem/999")
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "Workitem not found"
