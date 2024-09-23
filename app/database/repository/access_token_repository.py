from sqlmodel import Session

from app.database.models import AccessToken


from .database_repository import DatabaseRepository


class AccessTokenRepository(DatabaseRepository[AccessToken]):
    def __init__(self, session: Session) -> None:
        super().__init__(AccessToken, session)

