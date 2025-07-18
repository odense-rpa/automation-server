from typing import List, Optional

from sqlalchemy.sql import func
from sqlmodel import Session, select

from app.database.models import SessionLog

from .database_repository import DatabaseRepository, AbstractRepository

class AbstractSessionLogRepository(AbstractRepository[SessionLog]):
    def get_paginated(
        self,
        session_id: int,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
        include_deleted: bool = False,
    ) -> tuple[List[SessionLog], int]:
        raise NotImplementedError
    
    def get_logs_by_session_id(
        self,
        session_id: int,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[SessionLog]:
        raise NotImplementedError
    
    def count_logs_by_session_id(
        self, session_id: int, search: Optional[str] = None
    ) -> int:
        raise NotImplementedError
    
    def get_logs_by_workitem_id(self, workitem_id: int) -> List[SessionLog]:
        raise NotImplementedError


class SessionLogRepository(AbstractSessionLogRepository, DatabaseRepository[SessionLog]):
    def __init__(self, session: Session) -> None:
        super().__init__(SessionLog, session)

    def get_paginated(
        self,
        session_id: int,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
        include_deleted: bool = False,
    ) -> tuple[List[SessionLog], int]:
        query = select(SessionLog).where(
            SessionLog.session_id == session_id
        )

        if search:
            query = query.where(SessionLog.message.ilike(f"%{search}%"))

        # The original query for items already includes filters for session_id and search.
        # We create a new count_query based on SessionLog and apply the same filters.
        count_query = select(func.count()).select_from(SessionLog)
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
    ) -> List[SessionLog]:
        query = select(SessionLog).where(
            SessionLog.session_id == session_id
        )

        if search:
            query = query.where(SessionLog.message.contains(search))

        logs = self.session.exec(query.offset(skip).limit(limit)).all()
        return logs

    def count_logs_by_session_id(
        self, session_id: int, search: Optional[str] = None
    ) -> int:
        query = select(func.count()).where(SessionLog.session_id == session_id)

        if search:
            query = query.where(SessionLog.message.contains(search))

        return self.session.exec(query).first()

    def get_logs_by_workitem_id(self, workitem_id: int) -> List[SessionLog]:
        return self.session.scalars(
            select(SessionLog)
            .where(SessionLog.workitem_id == workitem_id)
            .order_by(SessionLog.created_at)
        ).all()
