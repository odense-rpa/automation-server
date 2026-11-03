import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.crypto import ENCRYPTION_PREFIX, dump_json
from app.database.models import Datastore

DOCUMENT = {
    "counts": {"2026-11-03": {"A": 12, "B": 9}},
    "teams": ["A", "B", "C", "D"],
    "note": "Æblegrød – “quotes” 🚀",
    "nothing": None,
}


async def add(session: AsyncSession, **fields) -> Datastore:
    datastore = Datastore(**fields)
    session.add(datastore)
    await session.commit()
    await session.refresh(datastore)
    return datastore


async def stored_data(session: AsyncSession, datastore_id: int) -> str:
    row = await session.execute(
        text("SELECT data FROM datastore WHERE id = :id"), {"id": datastore_id}
    )
    return row.scalar_one()


async def test_round_trip_without_key(session: AsyncSession, monkeypatch):
    monkeypatch.setattr(settings, "encryption_key", "")
    datastore = await add(session, name="state", data=DOCUMENT)

    # Without a key the document is stored as compact plaintext JSON
    assert await stored_data(session, datastore.id) == dump_json(DOCUMENT)

    session.expunge_all()  # force a fresh SELECT
    loaded = await session.get(Datastore, datastore.id)
    assert loaded.data == DOCUMENT
    assert loaded.version == 1


async def test_encrypted_at_rest(session: AsyncSession, monkeypatch):
    monkeypatch.setattr(settings, "encryption_key", "test-key")
    datastore = await add(session, name="state", data=DOCUMENT)

    stored = await stored_data(session, datastore.id)
    assert stored.startswith(ENCRYPTION_PREFIX)
    assert "counts" not in stored and "Æblegrød" not in stored

    session.expunge_all()  # force a fresh SELECT
    loaded = await session.get(Datastore, datastore.id)
    assert loaded.data == DOCUMENT


async def test_plaintext_rows_readable_after_key_is_configured(
    session: AsyncSession, monkeypatch
):
    # Written before a key was configured
    monkeypatch.setattr(settings, "encryption_key", "")
    datastore = await add(session, name="state", data=DOCUMENT)

    monkeypatch.setattr(settings, "encryption_key", "test-key")
    session.expunge_all()  # force a fresh SELECT
    loaded = await session.get(Datastore, datastore.id)
    assert loaded.data == DOCUMENT


async def test_name_unique_among_active_datastores(session: AsyncSession):
    await add(session, name="state")

    with pytest.raises(IntegrityError):
        await add(session, name="state")


async def test_deleted_name_can_be_reused(session: AsyncSession):
    first = await add(session, name="state", deleted=True)
    second = await add(session, name="state")
    # Names are case-sensitive, like credentials
    await add(session, name="State")

    rows = (
        await session.scalars(select(Datastore).where(Datastore.name == "state"))
    ).all()
    assert {d.id for d in rows} == {first.id, second.id}

    # Only one of them may be active
    with pytest.raises(IntegrityError):
        await add(session, name="state")


def test_dump_json_is_compact_and_utf8():
    assert dump_json({"a": [1, 2], "b": "ø"}) == '{"a":[1,2],"b":"ø"}'


# Encryption status and re-encryption (EncryptedColumnsMixin)


async def test_reencrypt_plaintext_datastores(session: AsyncSession, monkeypatch):
    from app.database.repository import DatastoreRepository

    # Written before a key was configured, including an empty document,
    # which is falsy in Python but still stored (as '{}')
    monkeypatch.setattr(settings, "encryption_key", "")
    full = await add(session, name="full", data=DOCUMENT)
    empty = await add(session, name="empty", data={})
    before = {full.id: (full.version, full.updated_at)}

    monkeypatch.setattr(settings, "encryption_key", "test-key")
    repository = DatastoreRepository(session)
    assert await repository.get_unencrypted_ids() == {full.id, empty.id}
    assert await repository.get_encrypted_ids() == set()

    assert await repository.reencrypt_unencrypted() == 2
    assert await repository.get_unencrypted_ids() == set()
    assert await repository.get_encrypted_ids() == {full.id, empty.id}
    for datastore_id in (full.id, empty.id):
        assert (await stored_data(session, datastore_id)).startswith(ENCRYPTION_PREFIX)

    # Re-encryption isn't a change to the document: version and updated_at
    # stay, so it never causes a conflict for a writer
    session.expunge_all()
    reloaded = await session.get(Datastore, full.id)
    assert (reloaded.version, reloaded.updated_at) == before[full.id]
    assert reloaded.data == DOCUMENT
    assert (await session.get(Datastore, empty.id)).data == {}


async def test_reencrypt_without_key_does_nothing(session: AsyncSession, monkeypatch):
    from app.database.repository import DatastoreRepository

    monkeypatch.setattr(settings, "encryption_key", "")
    await add(session, name="state", data=DOCUMENT)

    repository = DatastoreRepository(session)
    assert await repository.reencrypt_unencrypted() == 0
    assert len(await repository.get_unencrypted_ids()) == 1


async def test_can_decrypt_detects_a_changed_key(session: AsyncSession, monkeypatch):
    from app.database.repository import DatastoreRepository

    repository = DatastoreRepository(session)
    monkeypatch.setattr(settings, "encryption_key", "original-key")
    assert await repository.can_decrypt()  # nothing encrypted yet

    await add(session, name="state", data=DOCUMENT)
    assert await repository.can_decrypt()

    monkeypatch.setattr(settings, "encryption_key", "another-key")
    assert not await repository.can_decrypt()
    # Status keeps answering although the documents can't be read
    assert len(await repository.get_encrypted_ids()) == 1
