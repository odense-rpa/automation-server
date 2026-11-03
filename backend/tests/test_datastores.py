from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.crypto import ENCRYPTION_PREFIX


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
