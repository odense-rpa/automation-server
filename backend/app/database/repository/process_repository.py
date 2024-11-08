from sqlmodel import Session

from app.database.models import Process

from .database_repository import DatabaseRepository, AbstractRepository


class AbstractProcessRepository(AbstractRepository[Process]):
    pass


class ProcessRepository(AbstractProcessRepository, DatabaseRepository[Process]):
    def __init__(self, session: Session) -> None:
        super().__init__(Process, session)
