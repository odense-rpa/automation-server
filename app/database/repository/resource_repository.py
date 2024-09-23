from sqlmodel import Session, select

from app.database.models import Resource

from .database_repository import DatabaseRepository

class ResourceRepository(DatabaseRepository[Resource]):
    def __init__(self, session: Session) -> None:
        super().__init__(Resource, session)

    def get_by_fqdn(self, fqdn: str) -> Resource | None:
        return self.session.scalars(
            select(Resource).where(Resource.fqdn == fqdn)
        ).first()

    def get_available_resources(self) -> list[Resource]:
        return self.session.scalars(
            select(Resource)
            .where(Resource.available == True)  # noqa: E712
            .where(Resource.deleted == False)  # noqa: E712
        ).all()

