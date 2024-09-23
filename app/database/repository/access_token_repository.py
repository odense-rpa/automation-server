import secrets
from datetime import datetime, timedelta

from sqlmodel import Session

from app.database import models


from .database_repository import DatabaseRepository


class AccessTokenRepository(DatabaseRepository[models.AccessToken]):
    def __init__(self, session: Session) -> None:
        super().__init__(models.AccessToken, session)

    def generate_access_token(self) -> models.AccessToken:
        # Create a new access token
        token = models.AccessToken(
            token=secrets.token_urlsafe(32),
            expires_at=datetime.now() + timedelta(days=365),
        )

        return self.create(token.model_dump())
