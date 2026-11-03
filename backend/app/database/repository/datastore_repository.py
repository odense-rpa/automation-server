from datetime import datetime

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database.models import Datastore

from .database_repository import AbstractRepository, DatabaseRepository


class AbstractDatastoreRepository(AbstractRepository[Datastore]):
    async def get_by_name(self, name: str) -> Datastore | None:
        raise NotImplementedError

    async def compare_and_set(
        self, datastore_id: int, expected_version: int | None, values: dict
    ) -> Datastore | None:
        raise NotImplementedError


class DatastoreRepository(DatabaseRepository[Datastore]):
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
