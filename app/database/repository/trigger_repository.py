from sqlmodel import Session

from app.database.models import Trigger

from .database_repository import DatabaseRepository


class TriggerRepository(DatabaseRepository[Trigger]):
    def __init__(self, session: Session) -> None:
        super().__init__(Trigger, session)