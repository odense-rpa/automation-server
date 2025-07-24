from typing import List, Optional

from sqlalchemy.sql import func
from sqlmodel import Session, select

from app.database.models import AuditLog

from .database_repository import DatabaseRepository, AbstractRepository

class AbstractAuditLogRepository(AbstractRepository[AuditLog]):
    def get_paginated(
        self,
        session_id: int,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
        include_deleted: bool = False,
    ) -> tuple[List[AuditLog], int]:
        raise NotImplementedError
    
    def get_logs_by_session_id(
        self,
        session_id: int,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[AuditLog]:
        raise NotImplementedError
    
    def count_logs_by_session_id(
        self, session_id: int, search: Optional[str] = None
    ) -> int:
        raise NotImplementedError
    
    def get_logs_by_workitem_id(self, workitem_id: int) -> List[AuditLog]:
        raise NotImplementedError


class AuditLogRepository(AbstractAuditLogRepository, DatabaseRepository[AuditLog]):
    def __init__(self, session: Session) -> None:
        super().__init__(AuditLog, session)

    def get_paginated(
        self,
        session_id: int,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
        include_deleted: bool = False,
    ) -> tuple[List[AuditLog], int]:
        query = select(AuditLog).where(
            AuditLog.session_id == session_id
        )

        if search:
            query = query.where(AuditLog.message.ilike(f"%{search}%"))

        # The original query for items already includes filters for session_id and search.
        # We create a new count_query based on AuditLog and apply the same filters.
        count_query = select(func.count()).select_from(AuditLog)
        if query.whereclause is not None:
            count_query = count_query.where(query.whereclause)
            
        total_count = self.session.exec(count_query).first()

        return (
            list(self.session.exec(query.offset(skip).limit(limit)).all()),
            total_count,
        )

    def get_logs_by_session_id(
        self,
        session_id: int,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[AuditLog]:
        query = select(AuditLog).where(
            AuditLog.session_id == session_id
        )

        if search:
            query = query.where(AuditLog.message.contains(search))

        logs = self.session.exec(query.offset(skip).limit(limit)).all()
        return logs

    def count_logs_by_session_id(
        self, session_id: int, search: Optional[str] = None
    ) -> int:
        query = select(func.count()).where(AuditLog.session_id == session_id)

        if search:
            query = query.where(AuditLog.message.contains(search))

        return self.session.exec(query).first()

    def get_logs_by_workitem_id(self, workitem_id: int) -> List[AuditLog]:
        return self.session.scalars(
            select(AuditLog)
            .where(AuditLog.workitem_id == workitem_id)
            .order_by(AuditLog.created_at)
        ).all()
