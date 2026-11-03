import logging

from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import crypto
from app.database.crypto import ENCRYPTION_PREFIX
from app.database.repository import DatastoreRepository
from app.main import check_encryption


async def create(client: AsyncClient, name="state", data=None, description=""):
    response = await client.post(
        "/datastores",
        json={"name": name, "description": description, "data": data or {}},
    )
    assert response.status_code == 200, response.text
    return response.json()


# Create, read, list


async def test_create_and_read(client: AsyncClient):
    created = await create(client, data={"counts": {"A": 1}}, description="Team counts")

    assert created["version"] == 1
    assert created["size_bytes"] == len('{"counts":{"A":1}}')
    assert created["description"] == "Team counts"

    by_id = (await client.get(f"/datastores/{created['id']}")).json()
    by_name = (await client.get("/datastores/by_name/state")).json()
    assert by_id["data"] == by_name["data"] == {"counts": {"A": 1}}


async def test_list_has_no_documents(client: AsyncClient):
    await create(client, name="b", data={"x": 1})
    await create(client, name="a", data={"y": 2})

    listed = (await client.get("/datastores")).json()
    assert [d["name"] for d in listed] == ["a", "b"]
    assert all("data" not in d for d in listed)


async def test_unknown_datastore(client: AsyncClient):
    assert (await client.get("/datastores/999")).status_code == 404
    assert (await client.get("/datastores/by_name/nope")).status_code == 404


async def test_duplicate_name_is_rejected(client: AsyncClient):
    await create(client)
    response = await client.post("/datastores", json={"name": "state", "data": {}})
    assert response.status_code == 422


# Update by id (UI)


async def test_update_with_expected_version(client: AsyncClient):
    created = await create(client, data={"n": 1})
    url = f"/datastores/{created['id']}"

    ok = await client.put(url, json={"data": {"n": 2}, "expected_version": 1})
    assert ok.status_code == 200
    assert ok.json()["version"] == 2

    # A second writer that read version 1 is refused, not silently applied
    stale = await client.put(url, json={"data": {"n": 99}, "expected_version": 1})
    assert stale.status_code == 409
    assert (await client.get(url)).json()["data"] == {"n": 2}


async def test_update_without_expected_version_overwrites(client: AsyncClient):
    created = await create(client, data={"n": 1})
    url = f"/datastores/{created['id']}"

    response = await client.put(url, json={"data": {"n": 2}})
    assert response.status_code == 200
    assert response.json()["version"] == 2


async def test_update_name_and_description_keeps_data(client: AsyncClient):
    created = await create(client, data={"n": 1})
    url = f"/datastores/{created['id']}"

    response = await client.put(url, json={"name": "renamed", "description": "New"})
    body = response.json()
    assert body["name"] == "renamed" and body["description"] == "New"
    assert body["data"] == {"n": 1}


async def test_rename_to_existing_name_is_rejected(client: AsyncClient):
    await create(client, name="taken")
    other = await create(client, name="other")

    response = await client.put(f"/datastores/{other['id']}", json={"name": "taken"})
    assert response.status_code == 422


# Write by name (automations): create-on-write


async def test_write_by_name_creates_then_updates(client: AsyncClient):
    first = await client.put("/datastores/by_name/state", json={"data": {"n": 1}})
    assert first.status_code == 201
    assert first.json()["version"] == 1

    second = await client.put(
        "/datastores/by_name/state", json={"data": {"n": 2}, "expected_version": 1}
    )
    assert second.status_code == 200
    assert second.json()["version"] == 2
    assert second.json()["id"] == first.json()["id"]


async def test_write_by_name_expected_version_zero_means_must_not_exist(
    client: AsyncClient,
):
    created = await client.put(
        "/datastores/by_name/state", json={"data": {}, "expected_version": 0}
    )
    assert created.status_code == 201

    again = await client.put(
        "/datastores/by_name/state", json={"data": {}, "expected_version": 0}
    )
    assert again.status_code == 409


async def test_write_by_name_stale_version(client: AsyncClient):
    await client.put("/datastores/by_name/state", json={"data": {"n": 1}})
    await client.put("/datastores/by_name/state", json={"data": {"n": 2}})

    stale = await client.put(
        "/datastores/by_name/state", json={"data": {"n": 3}, "expected_version": 1}
    )
    assert stale.status_code == 409


async def test_write_by_name_expected_version_for_missing_datastore(
    client: AsyncClient,
):
    response = await client.put(
        "/datastores/by_name/state", json={"data": {}, "expected_version": 3}
    )
    assert response.status_code == 404


# Size limit


async def test_size_limit(client: AsyncClient, monkeypatch):
    monkeypatch.setattr(settings, "datastore_max_bytes", 20)

    # '{"text":"0123456789"}' is 21 bytes
    too_big = {"text": "0123456789"}
    fits = {"text": "012345678"}

    response = await client.post("/datastores", json={"name": "s", "data": too_big})
    assert response.status_code == 413

    created = await create(client, name="s", data=fits)
    assert created["size_bytes"] == 20

    response = await client.put(f"/datastores/{created['id']}", json={"data": too_big})
    assert response.status_code == 413
    response = await client.put("/datastores/by_name/s", json={"data": too_big})
    assert response.status_code == 413


async def test_size_counts_utf8_bytes(client: AsyncClient):
    created = await create(client, data={"t": "ø"})
    # '{"t":"ø"}' is 9 characters but 10 bytes
    assert created["size_bytes"] == 10


# Delete


async def test_delete(client: AsyncClient):
    created = await create(client, data={"n": 1})
    url = f"/datastores/{created['id']}"

    assert (await client.delete(url)).status_code == 204
    assert (await client.get(url)).status_code == 410
    assert (await client.put(url, json={"data": {}})).status_code == 410
    assert (await client.get("/datastores/by_name/state")).status_code == 404
    assert [d["name"] for d in (await client.get("/datastores")).json()] == []


async def test_deleted_name_is_recreated_by_write(client: AsyncClient):
    created = await create(client, data={"old": True})
    await client.delete(f"/datastores/{created['id']}")

    response = await client.put("/datastores/by_name/state", json={"data": {"new": 1}})
    assert response.status_code == 201
    assert response.json()["id"] != created["id"]
    assert response.json()["data"] == {"new": 1}


# Encryption


async def test_document_encrypted_at_rest(
    client: AsyncClient, session: AsyncSession, monkeypatch
):
    monkeypatch.setattr(settings, "encryption_key", "test-key")
    created = await create(client, data={"secret-ish": "value"})

    stored = (
        await session.execute(
            text("SELECT data FROM datastore WHERE id = :id"), {"id": created["id"]}
        )
    ).scalar_one()
    assert stored.startswith(ENCRYPTION_PREFIX)

    response = await client.get(f"/datastores/{created['id']}")
    assert response.json()["data"] == {"secret-ish": "value"}


# Encryption status and re-encryption


async def test_encryption_status_and_reencrypt(client: AsyncClient, monkeypatch):
    monkeypatch.setattr(settings, "encryption_key", "")
    await create(client, name="a", data={"n": 1})
    await create(client, name="b", data={})

    monkeypatch.setattr(settings, "encryption_key", "test-key")
    status = (await client.get("/datastores/encryption")).json()
    assert status == {
        "key_configured": True,
        "unencrypted_count": 2,
        "encrypted_count": 0,
        "decryptable": True,
    }

    result = await client.post("/datastores/reencrypt")
    assert result.json() == {"reencrypted": 2, "remaining": 0}

    status = (await client.get("/datastores/encryption")).json()
    assert status["unencrypted_count"] == 0 and status["encrypted_count"] == 2

    # Version unchanged: a writer holding version 1 isn't refused
    response = await client.put(
        "/datastores/by_name/a", json={"data": {"n": 2}, "expected_version": 1}
    )
    assert response.status_code == 200


async def test_reencrypt_without_key_is_refused(client: AsyncClient, monkeypatch):
    monkeypatch.setattr(settings, "encryption_key", "")
    response = await client.post("/datastores/reencrypt")
    assert response.status_code == 409


async def test_encryption_status_with_a_changed_key(client: AsyncClient, monkeypatch):
    monkeypatch.setattr(settings, "encryption_key", "original-key")
    await create(client, data={"n": 1})

    monkeypatch.setattr(settings, "encryption_key", "another-key")
    status = (await client.get("/datastores/encryption")).json()
    assert status["decryptable"] is False
    assert status["encrypted_count"] == 1


# Startup check


async def test_startup_reports_datastores(
    client: AsyncClient, session: AsyncSession, monkeypatch, caplog
):
    monkeypatch.setattr(settings, "encryption_key", "")
    await create(client, data={"n": 1})

    # Plaintext left over after a key is configured
    monkeypatch.setattr(settings, "encryption_key", "test-key")
    with caplog.at_level(logging.WARNING, logger="app.main"):
        await check_encryption(session)
    assert "1 datastore(s) are still stored as PLAINTEXT" in caplog.text
    assert "POST /datastores/reencrypt" in caplog.text

    # Encrypted, then the key is removed
    await client.post("/datastores/reencrypt")
    monkeypatch.setattr(settings, "encryption_key", "")
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger="app.main"):
        await check_encryption(session)
    assert "1 datastore(s) are encrypted but ENCRYPTION_KEY is not set" in caplog.text


# Review fixes: races, listing, validation


async def test_listing_works_when_documents_cannot_be_decrypted(
    client: AsyncClient, monkeypatch
):
    monkeypatch.setattr(settings, "encryption_key", "original-key")
    await create(client, data={"n": 1})

    monkeypatch.setattr(settings, "encryption_key", "another-key")
    response = await client.get("/datastores")
    assert response.status_code == 200
    assert [d["name"] for d in response.json()] == ["state"]

    # Reading the document itself explains the problem in datastore terms
    response = await client.get("/datastores/by_name/state")
    assert response.status_code == 500
    assert "These datastores are encrypted" in response.json()["detail"]
    assert "credentials" not in response.json()["detail"]


async def test_reencrypt_skips_a_row_written_meanwhile(
    client: AsyncClient, session: AsyncSession, monkeypatch
):
    monkeypatch.setattr(settings, "encryption_key", "")
    created = await create(client, data={"n": 1})
    monkeypatch.setattr(settings, "encryption_key", "test-key")

    # An automation writes {"n": 2} between re-encryption's read and write
    original = DatastoreRepository._read_stored

    async def read_then_concurrent_write(self, row_id):
        stored = await original(self, row_id)
        await self.session.execute(
            text("UPDATE datastore SET data = :data WHERE id = :id"),
            {"data": crypto.encrypt('{"n":2}'), "id": row_id},
        )
        return stored

    monkeypatch.setattr(DatastoreRepository, "_read_stored", read_then_concurrent_write)
    result = (await client.post("/datastores/reencrypt")).json()
    assert result == {"reencrypted": 0, "remaining": 0}

    # The concurrent write survives; the stale plaintext was not written back
    response = await client.get(f"/datastores/{created['id']}")
    assert response.json()["data"] == {"n": 2}


async def test_unconditional_write_by_name_survives_a_concurrent_create(
    client: AsyncClient, monkeypatch
):
    await create(client, data={"n": 1})

    # The first lookup misses the datastore another writer just created
    original = DatastoreRepository.get_by_name
    calls = []

    async def miss_once(self, name):
        calls.append(name)
        return None if len(calls) == 1 else await original(self, name)

    monkeypatch.setattr(DatastoreRepository, "get_by_name", miss_once)
    response = await client.put("/datastores/by_name/state", json={"data": {"n": 2}})
    assert response.status_code == 200
    assert response.json()["data"] == {"n": 2}


async def delete_before_first_write(monkeypatch):
    """Soft-delete the datastore just before the first compare-and-set."""
    original = DatastoreRepository.compare_and_set
    calls = []

    async def delete_then_write(self, datastore_id, expected_version, values):
        calls.append(datastore_id)
        if len(calls) == 1:
            await self.session.execute(
                text("UPDATE datastore SET deleted = true WHERE id = :id"),
                {"id": datastore_id},
            )
            # Committed, as by another request: the failed write's rollback
            # must not undo it
            await self.session.commit()
        return await original(self, datastore_id, expected_version, values)

    monkeypatch.setattr(DatastoreRepository, "compare_and_set", delete_then_write)


async def test_write_by_id_to_datastore_deleted_meanwhile(
    client: AsyncClient, monkeypatch
):
    created = await create(client, data={"n": 1})
    await delete_before_first_write(monkeypatch)

    response = await client.put(
        f"/datastores/{created['id']}", json={"data": {"n": 2}, "expected_version": 1}
    )
    assert response.status_code == 410


async def test_write_by_name_to_datastore_deleted_meanwhile(
    client: AsyncClient, monkeypatch
):
    await create(client, data={"n": 1})
    await delete_before_first_write(monkeypatch)

    # Unconditional: recreated, as a write after the delete would have done
    response = await client.put("/datastores/by_name/state", json={"data": {"n": 2}})
    assert response.status_code == 201
    assert response.json()["data"] == {"n": 2}


async def test_versioned_write_by_name_to_datastore_deleted_meanwhile(
    client: AsyncClient, monkeypatch
):
    await create(client, data={"n": 1})
    await delete_before_first_write(monkeypatch)

    response = await client.put(
        "/datastores/by_name/state", json={"data": {"n": 2}, "expected_version": 1}
    )
    assert response.status_code == 404


async def test_name_rules(client: AsyncClient):
    for name in ("a/b", " spaced", "spaced ", "", ".", "..", "a\x00b"):
        response = await client.post("/datastores", json={"name": name, "data": {}})
        assert response.status_code == 422, repr(name)

    created = await create(client, name="ok")
    response = await client.put(f"/datastores/{created['id']}", json={"name": "x/y"})
    assert response.status_code == 422


async def test_name_rules_apply_to_write_by_name(client: AsyncClient):
    response = await client.put("/datastores/by_name/%20spaced%20", json={"data": {}})
    assert response.status_code == 422
    response = await client.get("/datastores/by_name/%20spaced%20")
    assert response.status_code == 422


async def test_text_postgres_cannot_store_is_rejected(client: AsyncClient):
    headers = {"Content-Type": "application/json"}
    for body in (
        '{"name": "s", "description": "\\ud800", "data": {}}',
        '{"name": "\\ud800", "data": {}}',
        '{"name": "s", "description": "a\\u0000b", "data": {}}',
    ):
        response = await client.post("/datastores", content=body, headers=headers)
        assert response.status_code == 422, body


async def test_delete_and_recreate_when_document_cannot_be_decrypted(
    client: AsyncClient, monkeypatch
):
    monkeypatch.setattr(settings, "encryption_key", "original-key")
    created = await create(client, data={"n": 1})

    monkeypatch.setattr(settings, "encryption_key", "another-key")
    url = f"/datastores/{created['id']}"
    assert (await client.delete(url)).status_code == 204
    assert (await client.delete(url)).status_code == 410
    assert (await client.delete("/datastores/999")).status_code == 404

    # The process starts over with a fresh document under the current key
    response = await client.put("/datastores/by_name/state", json={"data": {"n": 2}})
    assert response.status_code == 201


async def test_document_that_is_not_json_is_rejected(client: AsyncClient):
    headers = {"Content-Type": "application/json"}
    for document in ('{"x": NaN}', '{"x": Infinity}', '{"x": "\\ud800"}'):
        response = await client.post(
            "/datastores",
            content=f'{{"name": "s", "data": {document}}}',
            headers=headers,
        )
        assert response.status_code == 422, document


async def test_expected_version_by_id_must_be_positive(client: AsyncClient):
    created = await create(client)
    response = await client.put(
        f"/datastores/{created['id']}", json={"data": {}, "expected_version": 0}
    )
    assert response.status_code == 422
