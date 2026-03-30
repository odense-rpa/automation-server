from typing import Optional

from app.api.v1.schemas import PaginatedResponse
from app.database.models import WorkItem
from app.database.repository import WorkqueueRepository
from app.enums import WorkItemStatus


class WorkqueueService:
    def __init__(self, workqueue_repository: WorkqueueRepository):
        self.repository = workqueue_repository

    async def search_workitems(
        self,
        workqueue_id: int,
        page: int = 1,
        size: int = 10,
        search: Optional[str] = None,
    ) -> PaginatedResponse[WorkItem]:
        skip = (page - 1) * size
        sessions, total_items = await self.repository.get_workitems_paginated(
            workqueue_id, search, skip, size
        )

        total_pages = (total_items + size - 1) // size

        response = PaginatedResponse[WorkItem](
            page=page,
            size=size,
            total_items=total_items,
            total_pages=total_pages,
            items=sessions,
        )

        return response

    async def count_pending_items(self, workqueue_id: int) -> int:
        # TODO: Implement deferred on this method
        return await self.repository.get_workitem_count(
            workqueue_id, status=WorkItemStatus.NEW
        )
