from typing import List, Optional

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from sqlmodel import select

import app.enums as enums
from app.database.models import Incident, Process

from .database_repository import AbstractRepository, DatabaseRepository


class AbstractIncidentRepository(AbstractRepository[Incident]):
    async def get_by_session_id(self, session_id: int) -> Optional[Incident]:
        raise NotImplementedError

    async def get_open_incidents(self) -> List[Incident]:
        raise NotImplementedError

    async def count_open_incidents(self) -> int:
        raise NotImplementedError

    async def dismiss_all_open(self) -> int:
        raise NotImplementedError

    async def get_paginated(
        self,
        search: Optional[str] = None,
        status: Optional[enums.IncidentStatus] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[List[Incident], int]:
        raise NotImplementedError


class IncidentRepository(AbstractIncidentRepository, DatabaseRepository[Incident]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Incident, session)

    async def get_by_session_id(self, session_id: int) -> Optional[Incident]:
        return (
            await self.session.scalars(
                select(Incident).where(Incident.session_id == session_id)
            )
        ).first()

    async def get_open_incidents(self) -> List[Incident]:
        return list(
            (
                await self.session.scalars(
                    select(Incident)
                    .where(Incident.status == enums.IncidentStatus.NEW)
                    .where(Incident.deleted == False)  # noqa: E712
                    .order_by(Incident.created_at.desc())
                )
            ).all()
        )

    async def count_open_incidents(self) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(Incident)
            .where(Incident.status == enums.IncidentStatus.NEW)
            .where(Incident.deleted == False)  # noqa: E712
        )
        return result.scalar_one() or 0

    async def dismiss_all_open(self) -> int:
        result = await self.session.execute(
            update(Incident)
            .where(Incident.status == enums.IncidentStatus.NEW)
            .where(Incident.deleted == False)  # noqa: E712
            .values(status=enums.IncidentStatus.DISMISSED)
        )
        await self.session.commit()
        return result.rowcount

    async def get_paginated(
        self,
        search: Optional[str] = None,
        status: Optional[enums.IncidentStatus] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[List[Incident], int]:
        query = select(Incident).where(Incident.deleted == False)  # noqa: E712

        if status is not None:
            query = query.where(Incident.status == status)

        if search:
            query = (
                query.join(Incident.session)
                .join(Process, Process.id == Incident.process_id)
                .filter(Process.name.ilike(f"%{search}%"))
            )

        query = query.order_by(Incident.created_at.desc())

        count_query = (
            select(func.count())
            .select_from(Incident)
            .where(
                Incident.deleted == False  # noqa: E712
            )
        )
        if status is not None:
            count_query = count_query.where(Incident.status == status)
        if search:
            count_query = (
                count_query.join(Incident.session)
                .join(Process, Process.id == Incident.process_id)
                .filter(Process.name.ilike(f"%{search}%"))
            )

        total_count = (await self.session.execute(count_query)).scalar_one()

        items = (await self.session.scalars(query.offset(skip).limit(limit))).all()

        return (list(items), total_count)
