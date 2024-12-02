from sqlmodel import Session, select

from app.database.models import Credential

from .database_repository import DatabaseRepository, AbstractRepository

class AbstractCredentialRepository(AbstractRepository[Credential]):
    pass

class CredentialRepository(DatabaseRepository[Credential]):
    def __init__(self, session: Session) -> None:
        super().__init__(Credential, session)

    def get_by_name(self, name: str) -> Credential:
        return self.session.exec(select(Credential).filter(Credential.name == name)).first()