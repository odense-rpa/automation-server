from sqlmodel import Session

from app.database.models import Credential

from .database_repository import DatabaseRepository

class CredentialRepository(DatabaseRepository[Credential]):
    def __init__(self, session: Session) -> None:
        super().__init__(Credential, session)


