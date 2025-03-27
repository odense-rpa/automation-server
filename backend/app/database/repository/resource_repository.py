import abc

from sqlmodel import Session, select, or_

from app.database.models import Resource, Session
from app.enums import SessionStatus

from .database_repository import DatabaseRepository, AbstractRepository


class AbstractResourceRepository(AbstractRepository[Resource]):
    @abc.abstractmethod
    def get_by_fqdn(self, fqdn: str) -> Resource | None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_available_resources(self) -> list[Resource]:
        raise NotImplementedError

    @abc.abstractmethod
    def is_resource_available(self, resource: Resource) -> bool:
        raise NotImplementedError

class ResourceRepository(AbstractResourceRepository, DatabaseRepository[Resource]):
    def __init__(self, session: Session) -> None:
        super().__init__(Resource, session)

    def get_by_fqdn(self, fqdn: str) -> Resource | None:
        return self.session.scalars(
            select(Resource).where(Resource.fqdn == fqdn)
        ).first()

    def get_available_resources(self) -> list[Resource]:
        resources = self.session.scalars(
            select(Resource)
            .where(Resource.deleted == False)  # noqa: E712
        ).all()
        
        return [resource for resource in resources if self.is_resource_available(resource)]

    def is_resource_available(self, resource: Resource) -> bool:
        
        sessions = self.session.scalars(
            select(Session)
            .where(Session.resource_id == resource.id)
            .where(or_(Session.status == SessionStatus.NEW, Session.status == SessionStatus.IN_PROGRESS))
        ).all()
        
        return len(sessions) == 0
        
        
