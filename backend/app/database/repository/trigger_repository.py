from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Trigger

from .database_repository import AbstractRepository, DatabaseRepository


class AbstractTriggerRepository(AbstractRepository[Trigger]):
    pass


class TriggerRepository(AbstractTriggerRepository, DatabaseRepository[Trigger]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Trigger, session)
