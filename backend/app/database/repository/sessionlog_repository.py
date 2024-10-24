from typing import List, Optional

from sqlalchemy.sql import func
from sqlmodel import Session, select

from app.database.models import SessionLog

from .database_repository import DatabaseRepository


class SessionLogRepository(DatabaseRepository[SessionLog]):
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
            query = query.where(SessionLog.message.contains(search))

        return [
            self.session.exec(query.offset(skip).limit(limit)).all(),
            self.session.exec(select(func.count()).select_from(query)).first(),
        ]

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
