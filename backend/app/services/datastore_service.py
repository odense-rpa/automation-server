from sqlalchemy.exc import IntegrityError

from app.database.crypto import dump_json
from app.database.models import Datastore
from app.database.repository import DatastoreRepository


class DatastoreTooLarge(Exception):
    def __init__(self, size: int, limit: int):
        super().__init__(f"Datastore document is {size} bytes, the limit is {limit}")


class DatastoreConflict(Exception):
    """The datastore changed since the caller read it (or already exists)."""


class DatastoreNameTaken(Exception):
    """Another datastore that isn't deleted already has this name."""


class DatastoreNotFound(Exception):
    pass


class DatastoreGone(Exception):
    """The datastore was deleted while it was being written."""


class DatastoreInvalid(Exception):
    """The document can't be stored as JSON."""


class DatastoreService:
    """Datastores: named JSON documents that automations keep state in.

    Writes carry an optional expected_version. When given, the write only
    succeeds if nobody else wrote in the meantime (DatastoreConflict
    otherwise), so concurrent runs can't silently overwrite each other.
    """

    def __init__(self, repository: DatastoreRepository, max_bytes: int):
        self.repository = repository
        self.max_bytes = max_bytes

    def _size(self, data: dict) -> int:
        try:
            size = len(dump_json(data).encode("utf-8"))
        except ValueError as error:
            # NaN/Infinity, or a lone surrogate (UnicodeEncodeError)
            raise DatastoreInvalid(f"Document is not valid JSON: {error}") from None
        if size > self.max_bytes:
            raise DatastoreTooLarge(size, self.max_bytes)
        return size

    async def create(self, name: str, description: str | None, data: dict) -> Datastore:
        size = self._size(data)
        try:
            return await self.repository.create(
                {
                    "name": name,
                    "description": description or "",
                    "data": data,
                    "size_bytes": size,
                    "version": 1,
                    "deleted": False,
                }
            )
        except IntegrityError:
            await self.repository.session.rollback()
            raise DatastoreNameTaken(name) from None

    async def write(
        self,
        datastore: Datastore,
        expected_version: int | None,
        data: dict | None = None,
        name: str | None = None,
        description: str | None = None,
    ) -> Datastore:
        """Update any of data, name and description; bumps the version."""
        values = {}
        if data is not None:
            values["data"] = data
            values["size_bytes"] = self._size(data)
        if name is not None:
            values["name"] = name
        if description is not None:
            values["description"] = description

        # Read before writing: a failed write rolls back, which expires
        # loaded objects, and touching them afterwards would need a reload
        datastore_id, current_name = datastore.id, datastore.name
        try:
            updated = await self.repository.compare_and_set(
                datastore_id, expected_version, values
            )
        except IntegrityError:
            await self.repository.session.rollback()
            raise DatastoreNameTaken(name) from None

        if updated is None:
            if not await self.repository.is_active(datastore_id):
                raise DatastoreGone(current_name)
            raise DatastoreConflict(
                f"Datastore '{current_name}' was changed by someone else"
            )
        return updated

    async def write_by_name(
        self, name: str, data: dict, expected_version: int | None
    ) -> tuple[Datastore, bool]:
        """Write a datastore by name, creating it if it doesn't exist.

        expected_version 0 means "must not exist yet". Without
        expected_version the write always succeeds (last writer wins), also
        when another writer creates or deletes the datastore at the same
        time: it is retried against what is there then. Returns the
        datastore and whether it was created.
        """
        for _ in range(3):
            existing = await self.repository.get_by_name(name)

            if existing is None:
                if expected_version not in (None, 0):
                    raise DatastoreNotFound(name)
                try:
                    return await self.create(name, "", data), True
                except DatastoreNameTaken:
                    # Created by a concurrent writer between our read and insert
                    if expected_version == 0:
                        raise DatastoreConflict(
                            f"Datastore '{name}' was created by someone else"
                        ) from None
                    continue

            if expected_version == 0:
                raise DatastoreConflict(f"Datastore '{name}' already exists")

            try:
                return await self.write(existing, expected_version, data=data), False
            except DatastoreGone:
                # Deleted between our read and write
                if expected_version is not None:
                    raise DatastoreNotFound(name) from None
                continue

        # Only reachable if creates and deletes keep racing this write
        raise DatastoreConflict(f"Datastore '{name}' keeps changing, try again")
