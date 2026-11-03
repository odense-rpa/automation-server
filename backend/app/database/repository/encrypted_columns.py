from sqlalchemy import text
from sqlalchemy.orm.attributes import flag_modified

from app.database import crypto
from app.database.crypto import ENCRYPTION_PREFIX


def _has_value(value) -> bool:
    """Whether a column holds something to encrypt.

    Not plain truthiness: an empty JSON document ({}) is falsy in Python but
    is still stored, and encrypted, as '{}'. None and '' are passed through
    unencrypted by crypto.encrypt, so there is nothing to rewrite.
    """
    return value is not None and value != ""


class EncryptedColumnsMixin:
    """Encryption status and re-encryption for a repository's encrypted columns.

    For repositories whose model has columns stored with EncryptedStr or
    EncryptedJSON. Subclasses set ``encrypted_columns``; the table name comes
    from the repository's model (``self.model``, set by DatabaseRepository).

    Stored values are read with raw SQL, bypassing the type decorators, so
    everything here keeps working when the configured key cannot decrypt
    them. Soft-deleted rows are included: their data is still on disk.
    """

    encrypted_columns: tuple[str, ...] = ()

    @property
    def _encrypted_table(self) -> str:
        return self.model.__tablename__

    async def get_unencrypted_ids(self) -> set[int]:
        """Ids of rows with at least one encrypted column stored as plaintext."""
        plaintext = " OR ".join(
            f"({column} IS NOT NULL AND {column} <> '' AND {column} NOT LIKE :prefix)"
            for column in self.encrypted_columns
        )
        result = await self.session.execute(
            text(f"SELECT id FROM {self._encrypted_table} WHERE {plaintext}"),
            {"prefix": f"{ENCRYPTION_PREFIX}%"},
        )
        return {row[0] for row in result}

    async def get_encrypted_ids(self) -> set[int]:
        """Ids of rows holding ciphertext, readable or not."""
        ciphertext = " OR ".join(
            f"{column} LIKE :prefix" for column in self.encrypted_columns
        )
        result = await self.session.execute(
            text(f"SELECT id FROM {self._encrypted_table} WHERE {ciphertext}"),
            {"prefix": f"{ENCRYPTION_PREFIX}%"},
        )
        return {row[0] for row in result}

    async def can_decrypt(self) -> bool:
        """Whether stored ciphertext is readable with the current key.

        True when there is no ciphertext to read. Probes a single row rather
        than the whole table: one unreadable value means the key is wrong for
        all of them.
        """
        columns = ", ".join(self.encrypted_columns)
        ciphertext = " OR ".join(
            f"{column} LIKE :prefix" for column in self.encrypted_columns
        )
        row = (
            await self.session.execute(
                text(
                    f"SELECT {columns} FROM {self._encrypted_table}"
                    f" WHERE {ciphertext} LIMIT 1"
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

    def mark_encrypted_columns_dirty(self, instance) -> None:
        """Force the encrypted columns to be rewritten on the next flush.

        Unchanged values are not marked dirty, so SQLAlchemy would skip their
        columns on UPDATE and leave pre-key plaintext in place.
        """
        for column in self.encrypted_columns:
            if _has_value(getattr(instance, column)):
                flag_modified(instance, column)

    async def _read_stored(self, row_id: int) -> dict:
        """A row's encrypted columns as stored (raw text, not decrypted)."""
        columns = ", ".join(self.encrypted_columns)
        query = text(f"SELECT {columns} FROM {self._encrypted_table} WHERE id = :id")
        result = await self.session.execute(query, {"id": row_id})
        return dict(result.mappings().one())

    async def _write_stored(self, row_id: int, values: dict) -> None:
        """Write raw text to a row's columns, bypassing the column types."""
        assignments = ", ".join(f"{column} = :{column}" for column in values)
        query = text(f"UPDATE {self._encrypted_table} SET {assignments} WHERE id = :id")
        await self.session.execute(query, {**values, "id": row_id})

    async def reencrypt_unencrypted(self) -> int:
        """Encrypt every value that is still stored as plaintext.

        Works on the stored text directly: read the plaintext with raw SQL,
        encrypt it, write it back. That is exactly what the column types
        would write, without loading rows through the ORM. Nothing else
        changes (no updated_at, no version): re-encryption is not a change
        to the data itself.

        Returns:
            The number of rows rewritten. Zero when no key is configured,
            since there is nothing to encrypt with.
        """
        if not crypto.is_configured():
            return 0

        ids = await self.get_unencrypted_ids()
        for row_id in ids:
            stored = await self._read_stored(row_id)
            # Only the plaintext columns: a row can hold one of each
            plaintext = {
                column: value
                for column, value in stored.items()
                if value and not value.startswith(ENCRYPTION_PREFIX)
            }
            encrypted = {
                column: crypto.encrypt(value) for column, value in plaintext.items()
            }
            await self._write_stored(row_id, encrypted)

        await self.session.commit()
        return len(ids)
