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
        EncryptedStr type decorator. Soft-deleted credentials are included:
        their secrets are still on disk.
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

    async def get_encrypted_ids(self) -> set[int]:
        """Return ids of credentials holding ciphertext, readable or not.

        Uses raw SQL, so it keeps working when the configured key cannot
        decrypt the values.
        """
        result = await self.session.execute(
            text(
                "SELECT id FROM credential"
                " WHERE username LIKE :prefix OR password LIKE :prefix"
            ),
            {"prefix": f"{ENCRYPTION_PREFIX}%"},
        )
        return {row[0] for row in result}

    async def can_decrypt(self) -> bool:
        """Return whether stored ciphertext is readable with the current key.

        True when there is no ciphertext to read. Probes a single row rather
        than the whole table: one unreadable value means the key is wrong for
        all of them.
        """
        row = (
            await self.session.execute(
                text(
                    "SELECT username, password FROM credential"
                    " WHERE username LIKE :prefix OR password LIKE :prefix"
                    " LIMIT 1"
                ),
                {"prefix": f"{ENCRYPTION_PREFIX}%"},
            )
        ).first()

        if row is None:
            return True

        try:
            for value in row:
                crypto.decrypt(value)
        except crypto.EncryptionKeyError:
            return False

        return True

    async def reencrypt_unencrypted(self) -> int:
        """Rewrite plaintext credentials so they are stored encrypted.

        Reading a plaintext value passes it through untouched, so marking the
        fields dirty and flushing is enough to re-write them as ciphertext.
        ``updated_at`` is deliberately left alone — re-encryption is not a
        change to the credential itself.

        Returns:
            The number of credentials rewritten. Zero when no key is
            configured, since writes would be plaintext again.
        """
        if not crypto.is_configured():
            return 0

        ids = await self.get_unencrypted_ids()
        if not ids:
            return 0

        for credential_id in ids:
            credential = await self.session.get(Credential, credential_id)
            if credential is None:
                continue

            for field in ("username", "password"):
                if getattr(credential, field):
                    flag_modified(credential, field)

        await self.session.commit()
        return len(ids)
