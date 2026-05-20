from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from sqlmodel import select

from app.database.models import AuditLog

from .database_repository import AbstractRepository, DatabaseRepository


class AbstractAuditLogRepository(AbstractRepository[AuditLog]):
    async def get_paginated(
        self,
        session_id: int,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
        include_deleted: bool = False,
    ) -> tuple[List[AuditLog], int]:
        raise NotImplementedError

    async def get_logs_by_session_id(
        self,
        session_id: int,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[AuditLog]:
        raise NotImplementedError

    async def count_logs_by_session_id(
        self, session_id: int, search: Optional[str] = None
    ) -> int:
        raise NotImplementedError

    async def get_logs_by_workitem_id(self, workitem_id: int) -> List[AuditLog]:
        raise NotImplementedError

    async def get_recent_logs_by_session_id(
        self, session_id: int, limit: int = 20
    ) -> List[AuditLog]:
        raise NotImplementedError


class AuditLogRepository(AbstractAuditLogRepository, DatabaseRepository[AuditLog]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(AuditLog, session)

    async def get_paginated(
        self,
        session_id: int,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
        include_deleted: bool = False,
    ) -> tuple[List[AuditLog], int]:
        query = select(AuditLog).where(AuditLog.session_id == session_id)

        if search:
            query = query.where(AuditLog.message.ilike(f"%{search}%"))

        count_query = select(func.count()).select_from(AuditLog)
        if query.whereclause is not None:
            count_query = count_query.where(query.whereclause)

        total_count = (await self.session.execute(count_query)).scalar_one()

        items = (await self.session.scalars(query.offset(skip).limit(limit))).all()

        return (list(items), total_count)

    async def get_logs_by_session_id(
        self,
        session_id: int,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[AuditLog]:
        query = select(AuditLog).where(AuditLog.session_id == session_id)

        if search:
            query = query.where(AuditLog.message.contains(search))

        logs = (await self.session.scalars(query.offset(skip).limit(limit))).all()
        return logs

    async def count_logs_by_session_id(
        self, session_id: int, search: Optional[str] = None
    ) -> int:
        query = select(func.count()).where(AuditLog.session_id == session_id)

        if search:
            query = query.where(AuditLog.message.contains(search))

        return (await self.session.execute(query)).scalar_one()

    async def get_logs_by_workitem_id(self, workitem_id: int) -> List[AuditLog]:
        return list(
            (
                await self.session.scalars(
                    select(AuditLog)
                    .where(AuditLog.workitem_id == workitem_id)
                    .order_by(AuditLog.created_at)
                )
            ).all()
        )

    async def get_recent_logs_by_session_id(
        self, session_id: int, limit: int = 20
    ) -> List[AuditLog]:
        return list(
            (
                await self.session.scalars(
                    select(AuditLog)
                    .where(AuditLog.session_id == session_id)
                    .order_by(AuditLog.event_timestamp.desc())
                    .limit(limit)
                )
            ).all()
        )
