import abc
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.types import String

from collections import defaultdict

from sqlalchemy import or_
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, delete, cast

from app.database.models import Workqueue, WorkItem

import app.enums as enums

from .database_repository import DatabaseRepository, AbstractRepository


class AbstractWorkqueueRepository(AbstractRepository[Workqueue]):
    @abc.abstractmethod
    async def get_workitem_count(self, workqueue_id: int, status: enums.WorkItemStatus):
        raise NotImplementedError

    @abc.abstractmethod
    async def get_all_workitem_counts(self) -> dict[int, dict[enums.WorkItemStatus, int]]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_workitems_paginated(
        self,
        workqueue_id: int,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
        include_deleted: bool = False,
    ) -> tuple[List[WorkItem], int]:
        raise NotImplementedError

    @abc.abstractmethod
    async def clear(
        self,
        workqueue_id: int,
        workitem_status: enums.WorkItemStatus | None,
        days_older_than: int | None,
    ):
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_reference(
        self,
        workqueue_id: int,
        reference: str,
        status: enums.WorkItemStatus | None = None,
    ) -> list[WorkItem]:
        raise NotImplementedError


class WorkqueueRepository(DatabaseRepository[Workqueue]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Workqueue, session)

    async def get_workitem_count(self, workqueue_id: int, status: enums.WorkItemStatus):
        result = await self.session.execute(
            select(func.count())
            .where(WorkItem.workqueue_id == workqueue_id)
            .where(WorkItem.status == status)
        )
        return result.scalar_one()

    async def get_all_workitem_counts(self) -> dict[int, dict[enums.WorkItemStatus, int]]:
        result = await self.session.execute(
            select(WorkItem.workqueue_id, WorkItem.status, func.count())
            .group_by(WorkItem.workqueue_id, WorkItem.status)
        )
        rows = result.all()

        counts: dict[int, dict[enums.WorkItemStatus, int]] = defaultdict(
            lambda: {s: 0 for s in enums.WorkItemStatus}
        )
        for workqueue_id, status, count in rows:
            counts[workqueue_id][status] = count

        return counts

    async def get_by_name(self, name: str) -> Workqueue:
        return (await self.session.scalars(
            select(Workqueue).filter(Workqueue.name == name)
        )).first()

    async def get_workitems_paginated(
        self,
        workqueue_id: int,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
        include_deleted: bool = False,
    ) -> tuple[List[WorkItem], int]:
        query = select(WorkItem).where(WorkItem.workqueue_id == workqueue_id)

        if search:
            query = query.where(
                or_(
                    WorkItem.reference.ilike(f"%{search}%"),
                    cast(WorkItem.status, String).ilike(f"%{search}%"),
                    cast(WorkItem.data, String).ilike(f"%{search}%"),
                )
            )
        query = query.order_by(WorkItem.updated_at.desc())

        count_query = select(func.count()).select_from(WorkItem)
        if query.whereclause is not None:
            count_query = count_query.where(query.whereclause)

        total_count = (await self.session.execute(count_query)).scalar_one()

        items = (await self.session.scalars(query.offset(skip).limit(limit))).all()

        return (list(items), total_count)

    async def clear(
        self,
        workqueue_id: int,
        workitem_status: enums.WorkItemStatus | None,
        days_older_than: int | None,
    ):
        query = delete(WorkItem).where(WorkItem.workqueue_id == workqueue_id)

        if workitem_status is not None:
            query = query.where(WorkItem.status == workitem_status)

        if days_older_than is not None:
            cutoff_date = datetime.now() - timedelta(days=days_older_than)
            query = query.where(WorkItem.created_at < cutoff_date)

        await self.session.execute(query)
        await self.session.commit()

    async def get_by_reference(
        self,
        workqueue_id: int,
        reference: str,
        status: enums.WorkItemStatus | None = None,
    ) -> list[WorkItem]:
        """Get work items by reference value within a specific workqueue, optionally filtered by status."""
        if not reference or reference.strip() == "":
            return []

        query = select(WorkItem).where(
            WorkItem.workqueue_id == workqueue_id,
            WorkItem.reference == reference
        )

        if status is not None:
            query = query.where(WorkItem.status == status)

        query = query.order_by(WorkItem.created_at.desc())

        return list(await self.session.scalars(query))
