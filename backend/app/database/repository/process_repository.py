from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Process

from .database_repository import DatabaseRepository, AbstractRepository


class AbstractProcessRepository(AbstractRepository[Process]):
    pass


class ProcessRepository(AbstractProcessRepository, DatabaseRepository[Process]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Process, session)
