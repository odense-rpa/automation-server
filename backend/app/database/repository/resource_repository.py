import abc

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, or_

from app.database.models import Resource, Session
from app.enums import SessionStatus

from .database_repository import DatabaseRepository, AbstractRepository


class AbstractResourceRepository(AbstractRepository[Resource]):
    @abc.abstractmethod
    async def get_by_fqdn(self, fqdn: str) -> Resource | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_available_resources(self) -> list[Resource]:
        raise NotImplementedError

    @abc.abstractmethod
    async def is_resource_available(self, resource: Resource) -> bool:
        raise NotImplementedError


class ResourceRepository(AbstractResourceRepository, DatabaseRepository[Resource]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Resource, session)

    async def get_by_fqdn(self, fqdn: str) -> Resource | None:
        return (
            await self.session.scalars(select(Resource).where(Resource.fqdn == fqdn))
        ).first()

    async def get_available_resources(self) -> list[Resource]:
        resources = (
            await self.session.scalars(
                select(Resource).where(Resource.deleted == False)  # noqa: E712
            )
        ).all()

        result = []
        for resource in resources:
            if await self.is_resource_available(resource):
                result.append(resource)
        return result

    async def is_resource_available(self, resource: Resource) -> bool:

        sessions = (
            await self.session.scalars(
                select(Session)
                .where(Session.resource_id == resource.id)
                .where(
                    or_(
                        Session.status == SessionStatus.NEW,
                        Session.status == SessionStatus.IN_PROGRESS,
                    )
                )
            )
        ).all()

        return len(sessions) == 0
