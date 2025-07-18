from typing import Optional
from datetime import datetime, timedelta

from app.api.v1.schemas import PaginatedResponse
from app.database.repository import SessionRepository, ResourceRepository
from app.database.models import Session
from app.enums import SessionStatus


class SessionService:
    def __init__(self, session_repository: SessionRepository, resource_repository: ResourceRepository):
        self.repository = session_repository
        self.resource_repository = resource_repository

    def search_sessions(
        self,
        page: int = 1,
        size: int = 10,
        search: Optional[str] = None,
        include_deleted: bool = False,
    ) -> PaginatedResponse[Session]:
        skip = (page - 1) * size
        sessions, total_items = self.repository.get_paginated(
            search, skip, size, include_deleted
        )
        # total_items = self.repository.count_all(search)
        total_pages = (total_items + size - 1) // size

        response = PaginatedResponse[Session](
            page=page,
            size=size,
            total_items=total_items,
            total_pages=total_pages,
            items=sessions,
        )

        return response

    def reschedule_orphaned_sessions(self):
        """This function iterates over all new sessions and checks if the resource is unavailable. If so, it removes the session from the resource."""

        sessions = self.repository.get_new_sessions()

        for session in sessions:
            if session.resource_id is None:
                continue

            resource = self.resource_repository.get(session.resource_id)

            if resource is None or resource.deleted:
                self.repository.update(
                    session, {"resource_id": None, "dispatched_at": None}
                )
                continue

    def flush_dangling_sessions(self):
        """This function iterates over all sessions that are in progress and marks them as failed if the resource is unavailable. 
        The sessions needs to have been dispatched at least 4 hours ago."""
        sessions = self.repository.get_active_sessions()

        sessions = [session for session in sessions if session.status == SessionStatus.IN_PROGRESS]

        for session in sessions:
            if (
                session.dispatched_at < datetime.now() - timedelta(hours=4)
            ):
                resource = self.resource_repository.get(session.resource_id)

                if resource is None or resource.deleted:
                    self.repository.update(session, {"status": "failed"})
                    continue

    def create_session(self, process_id: int, force: bool = False, parameters: str = None) -> Optional[Session]:
        """Create a new session for the given process.
        
        Args:
            process_id: ID of the process to create session for
            force: If True, create session even if one already exists
            parameters: Optional parameters for the session
            
        Returns:
            Created session or None if session already exists and force=False
        """
        sessions = self.repository.get_new_sessions()

        # If there is a new or in progress session for this process, return None unless forced
        if any(session.process_id == process_id for session in sessions) and not force:
            return None

        # Create a new session
        session = self.repository.create(
            {
                "process_id": process_id,
                "status": SessionStatus.NEW,
                "deleted": False,
                "dispatched_at": None,
                "parameters": parameters,
            }
        )

        return session
