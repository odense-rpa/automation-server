import secrets
from datetime import datetime, timedelta
from sqlmodel import Session

from app.database.models import AccessToken
from .database_repository import DatabaseRepository

class AccessTokenRepository(DatabaseRepository[AccessToken]):
    def __init__(self, session: Session) -> None:
        super().__init__(AccessToken, session)

    # TODO: Unit test this method
    def get_by_identifier(self, identifier: str) -> AccessToken:
        return (
            self.session.select(AccessToken)
            .filter(AccessToken.identifier == identifier)
            .first()
        )

    def create(self, identifier: str) -> AccessToken:
        # Generate a random 128 character string for the token
        token = secrets.token_urlsafe(128)

        access_token = AccessToken(
            identifier=identifier,
            expires_at=datetime.now() + timedelta(weeks=52),
            access_token=token,
        )
        self.session.add(access_token)
        self.session.commit()
        self.session.refresh(access_token)
        return access_token
