from typing import Optional

from app.api.v1.schemas import PaginatedResponse
from app.database.repository import SessionRepository
from app.database.models import Session


class SessionService:
    def __init__(self, session_repository: SessionRepository):
        self.repository = session_repository

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
