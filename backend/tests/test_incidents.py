from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from sqlmodel import Session

import app.enums as enums
import app.database.models as models

from . import generate_basic_data  # noqa: F401


def _create_failed_session(client: TestClient) -> int:
    """Move session 4 (which has resource_id=3) through IN_PROGRESS → FAILED and return its ID."""
    # Transition to IN_PROGRESS
    response = client.put(
        "/sessions/4/status",
        json={"status": enums.SessionStatus.IN_PROGRESS},
    )
    assert response.status_code == 200, response.text

    # Transition to FAILED
    response = client.put(
        "/sessions/4/status",
        json={"status": enums.SessionStatus.FAILED},
    )
    assert response.status_code == 200, response.text
    return 4


def test_list_incidents_empty(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/incidents")
    assert response.status_code == 200

    data = response.json()
    assert data["total_items"] == 0
    assert data["items"] == []


def test_incident_created_on_session_failure(session: Session, client: TestClient):
    generate_basic_data(session)

    _create_failed_session(client)

    response = client.get("/incidents")
    assert response.status_code == 200

    data = response.json()
    assert data["total_items"] == 1

    incident = data["items"][0]
    assert incident["session_id"] == 4
    assert incident["process_id"] == 1
    assert incident["status"] == enums.IncidentStatus.NEW
    assert incident["deleted"] is False


def test_incident_creation_is_idempotent(session: Session, client: TestClient):
    generate_basic_data(session)

    _create_failed_session(client)

    # Fail the same session again via direct DB manipulation and API call
    # Simulate by calling create_incidents_for_new_failures indirectly —
    # just confirm that listing still shows exactly 1 incident
    response = client.get("/incidents")
    assert response.json()["total_items"] == 1

    # Creating a second incident for the same session via the service
    from app.database.repository import IncidentRepository, AuditLogRepository, SessionRepository, ResourceRepository
    from app.services import SessionService, IncidentService

    repo = IncidentRepository(session)
    auditlog_repo = AuditLogRepository(session)
    session_repo = SessionRepository(session)
    resource_repo = ResourceRepository(session)

    svc = IncidentService(repo, auditlog_repo, session_repo, SessionService(session_repo, resource_repo))

    db_session = session_repo.get(4)
    incident_1 = svc.create_incident_for_session(db_session)
    incident_2 = svc.create_incident_for_session(db_session)

    assert incident_1 is not None
    assert incident_2 is not None
    assert incident_1.id == incident_2.id  # Same incident returned


def test_get_open_incidents(session: Session, client: TestClient):
    generate_basic_data(session)

    _create_failed_session(client)

    response = client.get("/incidents/open")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == enums.IncidentStatus.NEW


def test_get_incident_by_id(session: Session, client: TestClient):
    generate_basic_data(session)

    _create_failed_session(client)

    response = client.get("/incidents/1")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == 1
    assert data["session_id"] == 4
    assert data["status"] == enums.IncidentStatus.NEW


def test_get_incident_not_found(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/incidents/999")
    assert response.status_code == 404


def test_resolve_incident_dismiss(session: Session, client: TestClient):
    generate_basic_data(session)

    _create_failed_session(client)

    response = client.put(
        "/incidents/1/resolve",
        json={"status": enums.IncidentStatus.DISMISSED, "resolution_note": "False alarm"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == enums.IncidentStatus.DISMISSED
    assert data["resolution_note"] == "False alarm"

    # Confirm open incidents is now empty
    response = client.get("/incidents/open")
    assert response.json() == []


def test_resolve_incident_invalid_transition(session: Session, client: TestClient):
    generate_basic_data(session)

    _create_failed_session(client)

    # Dismiss the incident first
    client.put("/incidents/1/resolve", json={"status": enums.IncidentStatus.DISMISSED})

    # Try to transition again from DISMISSED
    response = client.put(
        "/incidents/1/resolve",
        json={"status": enums.IncidentStatus.RESCHEDULED},
    )
    assert response.status_code == 400


def test_resolve_incident_reschedule_creates_session(session: Session, client: TestClient):
    generate_basic_data(session)

    _create_failed_session(client)

    # Count sessions before
    response = client.get("/sessions/")
    sessions_before = response.json()["total_items"]

    response = client.put(
        "/incidents/1/resolve",
        json={"status": enums.IncidentStatus.RESCHEDULED, "resolution_note": "Retrying"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == enums.IncidentStatus.RESCHEDULED
    assert data["rescheduled_session_id"] is not None

    # Confirm a new session was created
    response = client.get("/sessions/")
    sessions_after = response.json()["total_items"]
    assert sessions_after == sessions_before + 1


def test_list_incidents_with_status_filter(session: Session, client: TestClient):
    generate_basic_data(session)

    _create_failed_session(client)

    # Filter by NEW - should return 1
    response = client.get("/incidents?status=new")
    assert response.status_code == 200
    assert response.json()["total_items"] == 1

    # Filter by DISMISSED - should return 0
    response = client.get("/incidents?status=dismissed")
    assert response.status_code == 200
    assert response.json()["total_items"] == 0

    # Dismiss the incident
    client.put("/incidents/1/resolve", json={"status": enums.IncidentStatus.DISMISSED})

    # Filter by DISMISSED - should now return 1
    response = client.get("/incidents?status=dismissed")
    assert response.json()["total_items"] == 1


def test_delete_incident(session: Session, client: TestClient):
    generate_basic_data(session)

    _create_failed_session(client)

    response = client.delete("/incidents/1")
    assert response.status_code == 200

    # Deleted incident should return 410
    response = client.get("/incidents/1")
    assert response.status_code == 410

    # Should not appear in listings
    response = client.get("/incidents")
    assert response.json()["total_items"] == 0


def test_get_failed_without_incident_ignores_old_sessions(session: Session, client: TestClient):
    generate_basic_data(session)

    from app.database.repository import SessionRepository

    session_repo = SessionRepository(session)

    # Create a failed session that is 20 days old
    old_session = session_repo.create({
        "process_id": 1,
        "status": enums.SessionStatus.FAILED,
        "deleted": False,
    })
    old_session.created_at = datetime.now() - timedelta(days=20)
    session.add(old_session)
    session.commit()

    results = session_repo.get_failed_without_incident()
    ids = [s.id for s in results]
    assert old_session.id not in ids


def test_get_failed_without_incident_includes_recent_sessions(session: Session, client: TestClient):
    generate_basic_data(session)

    from app.database.repository import SessionRepository

    session_repo = SessionRepository(session)

    recent_session = session_repo.create({
        "process_id": 1,
        "status": enums.SessionStatus.FAILED,
        "deleted": False,
    })

    results = session_repo.get_failed_without_incident()
    ids = [s.id for s in results]
    assert recent_session.id in ids


def test_error_trace_captured(session: Session, client: TestClient):
    generate_basic_data(session)

    # Session 3 has audit logs associated
    # Let's create a failed session that has logs and verify trace is captured

    # Create a session with process_id=1 and assign resource
    # Then add audit logs to it and fail it
    from app.database.repository import SessionRepository, AuditLogRepository
    from datetime import datetime

    session_repo = SessionRepository(session)
    auditlog_repo = AuditLogRepository(session)

    # Create new session
    new_session = session_repo.create({
        "process_id": 1,
        "status": enums.SessionStatus.IN_PROGRESS,
        "resource_id": 1,
        "dispatched_at": datetime.now(),
        "deleted": False,
    })

    # Add audit logs
    session.add(models.AuditLog(
        session_id=new_session.id,
        message="Starting process",
        level="INFO",
        logger_name="worker",
        event_timestamp=datetime.now(),
    ))
    session.add(models.AuditLog(
        session_id=new_session.id,
        message="RuntimeError: Division by zero",
        level="ERROR",
        logger_name="worker",
        exception_type="RuntimeError",
        exception_message="Division by zero",
        event_timestamp=datetime.now(),
    ))
    session.commit()

    # Fail the session via API
    response = client.put(
        f"/sessions/{new_session.id}/status",
        json={"status": enums.SessionStatus.FAILED},
    )
    assert response.status_code == 200

    # Get the incident - should have error_trace with the logs
    response = client.get("/incidents")
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
