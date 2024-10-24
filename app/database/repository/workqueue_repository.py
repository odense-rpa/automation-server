from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.sql import func
from sqlmodel import Session, select, delete

from app.database.models import Workqueue, WorkItem

import app.enums as enums

from .database_repository import DatabaseRepository


class WorkqueueRepository(DatabaseRepository[Workqueue]):
    def __init__(self, session: Session) -> None:
        super().__init__(Workqueue, session)

    def get_workitem_count(self, workqueue_id: int, status: enums.WorkItemStatus):
        return self.session.exec(
            select(func.count())
            .where(WorkItem.workqueue_id == workqueue_id)
            .where(WorkItem.status == status)
        ).first()

    def get_workitems_paginated(
        self,
        workqueue_id: int,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
        include_deleted: bool = False,
    ) -> tuple[List[WorkItem], int]:
        query = select(WorkItem).where(
            WorkItem.workqueue_id == workqueue_id
        )

        if search:
            query = query.where(
                or_(
                    WorkItem.reference.contains(search),
                    WorkItem.status.contains(search),
                    WorkItem.data.contains(search),
                )
            )
        query = query.order_by(WorkItem.updated_at.desc())
        return (
            list(self.session.exec(query.offset(skip).limit(limit)).all()),
            self.session.exec(select(func.count()).select_from(query)).first(),
        ]
    
    def clear(
            self, workqueue_id: int, 
            workitem_status: enums.WorkItemStatus | None, 
            days_older_than: int | None
        ):
        query = delete(WorkItem).where(WorkItem.workqueue_id == workqueue_id)
        
        if workitem_status is not None:
            query = query.where(WorkItem.status == workitem_status)        

        if days_older_than is not None:
            cutoff_date = datetime.now() - timedelta(days=days_older_than)
            query = query.where(WorkItem.created_at < cutoff_date)

        self.session.exec(query)
        self.session.commit()
        )
