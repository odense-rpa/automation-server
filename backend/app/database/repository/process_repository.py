from sqlmodel import Session

from app.database.models import Process

from .database_repository import DatabaseRepository

class ProcessRepository(DatabaseRepository[Process]):
    def __init__(self, session: Session) -> None:
        super().__init__(Process, session)
