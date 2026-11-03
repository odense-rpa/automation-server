from datetime import datetime

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import defer
from sqlmodel import select

from app.database.models import Datastore

from .database_repository import AbstractRepository, DatabaseRepository
from .encrypted_columns import EncryptedColumnsMixin


class AbstractDatastoreRepository(AbstractRepository[Datastore]):
    async def get_by_name(self, name: str) -> Datastore | None:
        raise NotImplementedError

    async def compare_and_set(
        self, datastore_id: int, expected_version: int | None, values: dict
    ) -> Datastore | None:
        raise NotImplementedError


class DatastoreRepository(EncryptedColumnsMixin, DatabaseRepository[Datastore]):
    encrypted_columns = ("data",)

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Datastore, session)

    async def get_by_name(self, name: str) -> Datastore | None:
        """The datastore with this name that isn't deleted, if any."""
        return (
            await self.session.scalars(
                select(Datastore).where(
                    Datastore.name == name,
                    Datastore.deleted == False,  # noqa: E712
                )
            )
        ).first()

    async def get_all_without_data(
        self, include_deleted: bool = False
    ) -> list[Datastore]:
        """All datastores by name, without loading their documents.

        For listings: documents can be large, and skipping them means the
        listing still works when they can't be decrypted. Don't touch
        ``data`` on the results; it isn't loaded.
        """
        query = (
            select(Datastore).options(defer(Datastore.data)).order_by(Datastore.name)
        )
        if not include_deleted:
            query = query.where(Datastore.deleted == False)  # noqa: E712
        return list((await self.session.scalars(query)).all())

    async def is_deleted(self, datastore_id: int) -> bool | None:
        """Whether the datastore is deleted; None if it doesn't exist.

        Reads only the flag, not the document.
        """
        return (
            await self.session.execute(
                select(Datastore.deleted).where(Datastore.id == datastore_id)
            )
        ).scalar_one_or_none()

    async def is_active(self, datastore_id: int) -> bool:
        """Whether the datastore exists and isn't deleted."""
        return await self.is_deleted(datastore_id) is False

    async def soft_delete(self, datastore_id: int) -> None:
        """Mark the datastore deleted without loading (or decrypting) it."""
        await self.session.execute(
            update(Datastore)
            .where(Datastore.id == datastore_id)
            .values(deleted=True, updated_at=datetime.now())
        )
        await self.session.commit()

    async def compare_and_set(
        self, datastore_id: int, expected_version: int | None, values: dict
    ) -> Datastore | None:
        """Write values and bump the version in one atomic UPDATE.

        With expected_version, the write only happens if the stored version
        still matches; None means "whatever is there" (last writer wins).
        Returns the updated datastore, or None when the version didn't match
        (or the datastore is deleted).
        """
        conditions = [
            Datastore.id == datastore_id,
            Datastore.deleted == False,  # noqa: E712
        ]
        if expected_version is not None:
            conditions.append(Datastore.version == expected_version)

        result = await self.session.execute(
            update(Datastore)
            .where(*conditions)
            .values(**values, version=Datastore.version + 1, updated_at=datetime.now())
            .returning(Datastore.id)
        )
        if result.scalar_one_or_none() is None:
            await self.session.rollback()
            return None

        await self.session.commit()
        # The identity map may hold the row as it was before the UPDATE
        return await self.session.get(Datastore, datastore_id, populate_existing=True)
