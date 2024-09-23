from sqlmodel import Session, select

from app.database.models import ClientCredential

from .database_repository import DatabaseRepository



class ClientCredentialRepository(DatabaseRepository[ClientCredential]):
    def __init__(self, session: Session) -> None:
        super().__init__(ClientCredential, session)

    def get_by_client_id(self, client_id: str) -> ClientCredential | None:
        return self.session.scalars(
            select(ClientCredential).where(
                ClientCredential.client_id == client_id
            )
        ).first()
        
