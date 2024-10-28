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

            resource = self.repository.get_resource(session.resource_id)

            if resource is None or not resource.available:
                self.repository.update(
                    session, {"resource_id": None, "dispatched_at": None}
                )
                continue

    def flush_dangling_sessions(self):
        """This function iterates over all sessions that are in progress and marks them as failed if the resource is unavailable. 
        The sessions needs to have been dispatched at least 4 hours ago."""
        sessions = self.repository.get_active_sessions()

        for session in sessions:
            if (
                session.dispatched_at < datetime.now() - timedelta(hours=4)
                and session.status == SessionStatus.IN_PROGRESS
            ):
                resource = self.resource_repository.get(session.resource_id)

                if resource is None or not resource.available:
                    self.repository.update(session, {"status": "failed"})
                    continue
