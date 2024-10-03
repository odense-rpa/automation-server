from typing import Optional

from app.api.v1.schemas import PaginatedResponse
from app.database.repository import SessionLogRepository
from app.database.models import SessionLog


class SessionLogService:
    def __init__(self, session_repository: SessionLogRepository):
        self.repository = session_repository

    def search_logs(
        self,
        session_id: int,
        page: int = 1,
        size: int = 10,
        search: Optional[str] = None,
    ) -> PaginatedResponse[SessionLog]:
        skip = (page - 1) * size
        sessions, total_items = self.repository.get_paginated(
            session_id, search, skip, size
        )

        total_pages = (total_items + size - 1) // size

        response = PaginatedResponse[SessionLog](
            page=page,
            size=size,
            total_items=total_items,
            total_pages=total_pages,
            items=sessions,
        )

        return response

    def get_by_workitem(self, workitem_id: int) -> list[SessionLog]:
        return self.repository.get_logs_by_workitem_id(workitem_id)
