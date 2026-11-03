from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import crypto
from app.database.models import Credential

from .database_repository import AbstractRepository, DatabaseRepository
from .encrypted_columns import EncryptedColumnsMixin


class AbstractCredentialRepository(AbstractRepository[Credential]):
    pass


class CredentialRepository(EncryptedColumnsMixin, DatabaseRepository[Credential]):
    encrypted_columns = ("username", "password")

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Credential, session)

    async def update(self, instance: Credential, data: dict) -> Credential:
        for field, value in data.items():
            setattr(instance, field, value)

        # Force a rewrite so saving a credential always encrypts it, even
        # when its values are unchanged
        if crypto.is_configured():
            self.mark_encrypted_columns_dirty(instance)

        return await super().update(instance, {})

    async def get_by_name(self, name: str) -> Credential:
        return (
            await self.session.scalars(
                select(Credential).filter(Credential.name == name)
            )
        ).first()
