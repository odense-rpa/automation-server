from typing import Optional

from app.api.v1.schemas import PaginatedResponse
from app.database.repository import AuditLogRepository
from app.database.models import AuditLog


class AuditLogService:
    def __init__(self, audit_repository: AuditLogRepository):
        self.repository = audit_repository

    def search_logs(
        self,
        session_id: int,
        page: int = 1,
        size: int = 10,
        search: Optional[str] = None,
    ) -> PaginatedResponse[AuditLog]:
        skip = (page - 1) * size
        logs, total_items = self.repository.get_paginated(
            session_id, search, skip, size
        )

        total_pages = (total_items + size - 1) // size

        response = PaginatedResponse[AuditLog](
            page=page,
            size=size,
            total_items=total_items,
            total_pages=total_pages,
            items=logs,
        )

        return response

    def get_by_workitem(self, workitem_id: int) -> list[AuditLog]:
        return self.repository.get_logs_by_workitem_id(workitem_id)
