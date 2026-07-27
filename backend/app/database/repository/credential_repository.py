from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from sqlmodel import select

from app.database import crypto
from app.database.crypto import ENCRYPTION_PREFIX
from app.database.models import Credential

from .database_repository import AbstractRepository, DatabaseRepository


class AbstractCredentialRepository(AbstractRepository[Credential]):
    pass


class CredentialRepository(DatabaseRepository[Credential]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Credential, session)

    async def update(self, instance: Credential, data: dict) -> Credential:
        for field, value in data.items():
            setattr(instance, field, value)

        # Unchanged values are not marked dirty, so SQLAlchemy would skip
        # their columns on UPDATE and leave pre-key plaintext in place.
        # Force a rewrite so saving a credential always encrypts it.
        if crypto.is_configured():
            for field in ("username", "password"):
                if getattr(instance, field):
                    flag_modified(instance, field)

        return await super().update(instance, {})

    async def get_by_name(self, name: str) -> Credential:
        return (
            await self.session.scalars(
                select(Credential).filter(Credential.name == name)
            )
        ).first()

    async def get_unencrypted_ids(self) -> set[int]:
        """Return ids of credentials whose username or password is stored as plaintext.

        Uses raw SQL to read the stored values directly, bypassing the
        EncryptedStr type decorator.
        """
        result = await self.session.execute(
            text(
                "SELECT id FROM credential"
                " WHERE (username IS NOT NULL AND username <> ''"
                "        AND username NOT LIKE :prefix)"
                "    OR (password IS NOT NULL AND password <> ''"
                "        AND password NOT LIKE :prefix)"
            ),
            {"prefix": f"{ENCRYPTION_PREFIX}%"},
        )
        return {row[0] for row in result}
