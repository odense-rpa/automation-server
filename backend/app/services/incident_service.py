import logging
from typing import Optional

from app.api.v1.schemas import PaginatedResponse
from app.database.models import Incident, Session
from app.database.repository import (
    IncidentRepository,
    AuditLogRepository,
    SessionRepository,
)
from app.enums import IncidentStatus
from app.services.session_service import SessionService

logger = logging.getLogger(__name__)


class IncidentService:
    def __init__(
        self,
        incident_repository: IncidentRepository,
        auditlog_repository: AuditLogRepository,
        session_repository: SessionRepository,
        session_service: SessionService,
    ):
        self.repository = incident_repository
        self.auditlog_repository = auditlog_repository
        self.session_repository = session_repository
        self.session_service = session_service

    async def create_incident_for_session(self, session: Session) -> Optional[Incident]:
        """Create an incident for a failed session. Idempotent — returns existing incident if one exists."""
        existing = await self.repository.get_by_session_id(session.id)
        if existing is not None:
            return existing

        logs = list(
            reversed(
                await self.auditlog_repository.get_recent_logs_by_session_id(session.id)
            )
        )
        error_trace = [
            {
                "message": log.message,
                "level": log.level,
                "logger_name": log.logger_name,
                "module": log.module,
                "function_name": log.function_name,
                "line_number": log.line_number,
                "exception_type": log.exception_type,
                "exception_message": log.exception_message,
                "traceback": log.traceback,
                "event_timestamp": log.event_timestamp.isoformat()
                if log.event_timestamp
                else None,
            }
            for log in logs
        ]

        return await self.repository.create(
            {
                "session_id": session.id,
                "process_id": session.process_id,
                "status": IncidentStatus.NEW,
                "error_trace": error_trace,
                "deleted": False,
            }
        )

    async def create_incidents_for_new_failures(self) -> int:
        """Find all FAILED sessions without incidents and create incidents for them.

        Returns the number of incidents created.
        """
        failed_sessions = await self.session_repository.get_failed_without_incident()

        count = 0
        for session in failed_sessions:
            try:
                await self.create_incident_for_session(session)
                count += 1
            except Exception as e:
                logger.error(f"Failed to create incident for session {session.id}: {e}")

        return count

    async def resolve_incident(
        self,
        incident: Incident,
        status: IncidentStatus,
        note: Optional[str] = None,
    ) -> Incident:
        """Resolve an incident by transitioning to DISMISSED or RESCHEDULED.

        If RESCHEDULED, creates a new session for the same process.
        """
        if not incident.status.can_transition_to(status):
            raise ValueError(
                f"Cannot transition incident from {incident.status} to {status}"
            )

        update_data: dict = {"status": status}
        if note is not None:
            update_data["resolution_note"] = note

        if status == IncidentStatus.RESCHEDULED:
            original_session = await self.session_repository.get(incident.session_id)
            parameters = original_session.parameters if original_session else None

            new_session = await self.session_service.create_session(
                incident.process_id, force=True, parameters=parameters
            )
            if new_session is not None:
                update_data["rescheduled_session_id"] = new_session.id

        return await self.repository.update(incident, update_data)

    async def dismiss_all_open(self) -> int:
        """Dismiss all open (NEW) incidents. Returns the count dismissed."""
        return await self.repository.dismiss_all_open()

    async def search_incidents(
        self,
        page: int = 1,
        size: int = 50,
        search: Optional[str] = None,
        status: Optional[IncidentStatus] = None,
    ) -> PaginatedResponse[Incident]:
        skip = (page - 1) * size
        incidents, total_items = await self.repository.get_paginated(
            search, status, skip, size
        )
        total_pages = (total_items + size - 1) // size

        return PaginatedResponse[Incident](
            page=page,
            size=size,
            total_items=total_items,
            total_pages=total_pages,
            items=incidents,
        )
