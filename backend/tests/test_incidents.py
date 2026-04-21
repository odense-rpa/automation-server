from datetime import datetime, timedelta

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import app.database.models as models
import app.enums as enums

from . import generate_basic_data  # noqa: F401


async def _create_failed_session(client: AsyncClient) -> int:
    """Move session 4 (which has resource_id=3) through IN_PROGRESS → FAILED and return its ID."""
    # Transition to IN_PROGRESS
    response = await client.put(
        "/sessions/4/status",
        json={"status": enums.SessionStatus.IN_PROGRESS},
    )
    assert response.status_code == 200, response.text

    # Transition to FAILED
    response = await client.put(
        "/sessions/4/status",
        json={"status": enums.SessionStatus.FAILED},
    )
    assert response.status_code == 200, response.text
    return 4


async def test_list_incidents_empty(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/incidents")
    assert response.status_code == 200

    data = response.json()
    assert data["total_items"] == 0
    assert data["items"] == []


async def test_incident_created_on_session_failure(
    session: AsyncSession, client: AsyncClient
):
    await generate_basic_data(session)

    await _create_failed_session(client)

    response = await client.get("/incidents")
    assert response.status_code == 200

    data = response.json()
    assert data["total_items"] == 1

    incident = data["items"][0]
    assert incident["session_id"] == 4
    assert incident["process_id"] == 1
    assert incident["status"] == enums.IncidentStatus.NEW
    assert incident["deleted"] is False


async def test_incident_creation_is_idempotent(
    session: AsyncSession, client: AsyncClient
):
    await generate_basic_data(session)

    await _create_failed_session(client)

    # Fail the same session again via direct DB manipulation and API call
    # Simulate by calling create_incidents_for_new_failures indirectly —
    # just confirm that listing still shows exactly 1 incident
    response = await client.get("/incidents")
    assert response.json()["total_items"] == 1

    # Creating a second incident for the same session via the service
    from app.database.repository import (
        AuditLogRepository,
        IncidentRepository,
        ResourceRepository,
        SessionRepository,
    )
    from app.services import IncidentService, SessionService

    repo = IncidentRepository(session)
    auditlog_repo = AuditLogRepository(session)
    session_repo = SessionRepository(session)
    resource_repo = ResourceRepository(session)

    svc = IncidentService(
        repo, auditlog_repo, session_repo, SessionService(session_repo, resource_repo)
    )

    db_session = await session_repo.get(4)
    incident_1 = await svc.create_incident_for_session(db_session)
    incident_2 = await svc.create_incident_for_session(db_session)

    assert incident_1 is not None
    assert incident_2 is not None
    assert incident_1.id == incident_2.id  # Same incident returned


async def test_get_open_incidents(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    await _create_failed_session(client)

    response = await client.get("/incidents/open")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == enums.IncidentStatus.NEW


async def test_get_incident_by_id(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    await _create_failed_session(client)

    response = await client.get("/incidents/1")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == 1
    assert data["session_id"] == 4
    assert data["status"] == enums.IncidentStatus.NEW


async def test_get_incident_not_found(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/incidents/999")
    assert response.status_code == 404


async def test_resolve_incident_dismiss(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    await _create_failed_session(client)

    response = await client.put(
        "/incidents/1/resolve",
        json={
            "status": enums.IncidentStatus.DISMISSED,
            "resolution_note": "False alarm",
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == enums.IncidentStatus.DISMISSED
    assert data["resolution_note"] == "False alarm"

    # Confirm open incidents is now empty
    response = await client.get("/incidents/open")
    assert response.json() == []


async def test_resolve_incident_invalid_transition(
    session: AsyncSession, client: AsyncClient
):
    await generate_basic_data(session)

    await _create_failed_session(client)

    # Dismiss the incident first
    await client.put(
        "/incidents/1/resolve", json={"status": enums.IncidentStatus.DISMISSED}
    )

    # Try to transition again from DISMISSED
    response = await client.put(
        "/incidents/1/resolve",
        json={"status": enums.IncidentStatus.RESCHEDULED},
    )
    assert response.status_code == 400


async def test_resolve_incident_reschedule_creates_session(
    session: AsyncSession, client: AsyncClient
):
    await generate_basic_data(session)

    await _create_failed_session(client)

    # Count sessions before
    response = await client.get("/sessions/")
    sessions_before = response.json()["total_items"]

    response = await client.put(
        "/incidents/1/resolve",
        json={
            "status": enums.IncidentStatus.RESCHEDULED,
            "resolution_note": "Retrying",
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == enums.IncidentStatus.RESCHEDULED
    assert data["rescheduled_session_id"] is not None

    # Confirm a new session was created
    response = await client.get("/sessions/")
    sessions_after = response.json()["total_items"]
    assert sessions_after == sessions_before + 1


async def test_list_incidents_with_status_filter(
    session: AsyncSession, client: AsyncClient
):
    await generate_basic_data(session)

    await _create_failed_session(client)

    # Filter by NEW - should return 1
    response = await client.get("/incidents?status=new")
    assert response.status_code == 200
    assert response.json()["total_items"] == 1

    # Filter by DISMISSED - should return 0
    response = await client.get("/incidents?status=dismissed")
    assert response.status_code == 200
    assert response.json()["total_items"] == 0

    # Dismiss the incident
    await client.put(
        "/incidents/1/resolve", json={"status": enums.IncidentStatus.DISMISSED}
    )

    # Filter by DISMISSED - should now return 1
    response = await client.get("/incidents?status=dismissed")
    assert response.json()["total_items"] == 1


async def test_delete_incident(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    await _create_failed_session(client)

    response = await client.delete("/incidents/1")
    assert response.status_code == 200

    # Deleted incident should return 410
    response = await client.get("/incidents/1")
    assert response.status_code == 410

    # Should not appear in listings
    response = await client.get("/incidents")
    assert response.json()["total_items"] == 0


async def test_get_failed_without_incident_ignores_old_sessions(
    session: AsyncSession, client: AsyncClient
):
    await generate_basic_data(session)

    from app.database.repository.session_repository import SessionRepository

    old_session = models.Session(
        process_id=1,
        status=enums.SessionStatus.FAILED,
        deleted=False,
        created_at=datetime.now() - timedelta(days=20),
        updated_at=datetime.now(),
    )
    session.add(old_session)
    await session.commit()
    await session.refresh(old_session)

    session_repo = SessionRepository(session)
    results = await session_repo.get_failed_without_incident()
    ids = [s.id for s in results]
    assert old_session.id not in ids


async def test_get_failed_without_incident_includes_recent_sessions(
    session: AsyncSession, client: AsyncClient
):
    await generate_basic_data(session)

    from app.database.repository.session_repository import SessionRepository

    recent_session = models.Session(
        process_id=1,
        status=enums.SessionStatus.FAILED,
        deleted=False,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    session.add(recent_session)
    await session.commit()
    await session.refresh(recent_session)

    session_repo = SessionRepository(session)
    results = await session_repo.get_failed_without_incident()
    ids = [s.id for s in results]
    assert recent_session.id in ids


async def test_error_trace_captured(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    # Session 3 has audit logs associated
    # Let's create a failed session that has logs and verify trace is captured

    # Create a session with process_id=1 and assign resource
    # Then add audit logs to it and fail it
    from datetime import datetime

    from app.database.repository import SessionRepository

    session_repo = SessionRepository(session)

    # Create new session
    new_session = await session_repo.create(
        {
            "process_id": 1,
            "status": enums.SessionStatus.IN_PROGRESS,
            "resource_id": 1,
            "dispatched_at": datetime.now(),
            "deleted": False,
        }
    )

    # Add audit logs
    session.add(
        models.AuditLog(
            session_id=new_session.id,
            message="Starting process",
            level="INFO",
            logger_name="worker",
            event_timestamp=datetime.now(),
        )
    )
    session.add(
        models.AuditLog(
            session_id=new_session.id,
            message="RuntimeError: Division by zero",
            level="ERROR",
            logger_name="worker",
            exception_type="RuntimeError",
            exception_message="Division by zero",
            event_timestamp=datetime.now(),
        )
    )
    await session.commit()

    # Fail the session via API
    response = await client.put(
        f"/sessions/{new_session.id}/status",
        json={"status": enums.SessionStatus.FAILED},
    )
    assert response.status_code == 200

    # Get the incident - should have error_trace with the logs
    response = await client.get("/incidents")
    data = response.json()

    # Find incident for our session
    incident = next(
        (i for i in data["items"] if i["session_id"] == new_session.id), None
    )
    assert incident is not None
    assert len(incident["error_trace"]) == 2

    # Verify trace content (most recent first)
    error_entry = next(
        (e for e in incident["error_trace"] if e["level"] == "ERROR"), None
    )
    assert error_entry is not None
    assert error_entry["exception_type"] == "RuntimeError"
    assert error_entry["message"] == "RuntimeError: Division by zero"
