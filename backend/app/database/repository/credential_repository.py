from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database.models import Credential

from .database_repository import DatabaseRepository, AbstractRepository

class AbstractCredentialRepository(AbstractRepository[Credential]):
    pass

class CredentialRepository(DatabaseRepository[Credential]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Credential, session)

    async def get_by_name(self, name: str) -> Credential:
        return (await self.session.scalars(select(Credential).filter(Credential.name == name))).first()
