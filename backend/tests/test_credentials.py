from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

import app.database.models as models
from app.config import settings

from . import generate_basic_data  # noqa: F401


async def test_get_credentials(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/credentials/")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["name"] == "Secret credential"
    assert data[0]["username"] == "Secret username"
    assert data[0]["deleted"] is False

    response = await client.get("/credentials/?include_deleted=true")
    data = response.json()
    assert len(data) == 2

    assert data[1]["name"] == "Secret deleted credential"
    assert data[1]["username"] == "Secret deleted username"
    assert data[1]["deleted"] is True


async def test_get_credential(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/credentials/1")

    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Secret credential"
    assert data["username"] == "Secret username"
    assert data["deleted"] is False

    response = await client.get("/credentials/2")

    assert response.status_code == 410


async def test_update_credential(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.put(
        "/credentials/1",
        json={
            "name": "Secret credential",
            "username": "Secret username",
            "password": "New password",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Secret credential"
    assert data["username"] == "Secret username"
    assert data["password"] == "New password"

    response = await client.put(
        "/credentials/2",
        json={
            "name": "Secret deleted credential",
            "username": "Secret deleted username",
            "password": "New password",
            "description": "New description",
        },
    )

    assert response.status_code == 410


async def test_create_credential(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.post(
        "/credentials/",
        json={
            "name": "New credential",
            "username": "New username",
            "password": "New password",
        },
    )

    assert response.status_code == 200


async def test_delete_credential(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.delete("/credentials/1")

    assert response.status_code == 204

    # Verify against the database

    credential = await session.get(models.Credential, 1)
    assert credential.deleted is True

    response = await client.delete("/credentials/2")

    assert response.status_code == 410


async def test_retrieve_existing_credential_by_name(
    session: AsyncSession, client: AsyncClient
):
    await generate_basic_data(session)

    response = await client.get("/credentials/by_name/Secret credential")
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Secret credential"
    assert data["username"] == "Secret username"
    assert data["deleted"] is False


async def test_credential_not_found(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/credentials/by_name/nonexistent_credential")

    assert response.status_code == 404
    assert response.json() == {"detail": "Credential not found"}


async def test_credential_deleted(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/credentials/by_name/Secret deleted credential")

    assert response.status_code == 410
    assert response.json() == {"detail": "Credential is gone"}


async def test_case_sensitivity(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/credential/by_name/SeCreT cRedeNtiAl")
    assert response.status_code == 404  # Assuming case-sensitive


async def test_empty_credential_name(session: AsyncSession, client: AsyncClient):
    response = await client.get("/credential/by_name/")
    assert response.status_code == 404  # Assuming FastAPI route validation catches this


async def test_insert_non_unique_named_credential(
    session: AsyncSession, client: AsyncClient
):
    await generate_basic_data(session)

    response = await client.post(
        "/credentials/",
        json={
            "name": "Secret credential",
            "username": "New username",
            "password": "New password",
        },
    )

    assert response.status_code == 422


async def test_create_credential_with_invalid_json_data(
    session: AsyncSession, client: AsyncClient
):
    response = await client.post(
        "/credentials/",
        json={
            "name": "New credential",
            "username": "New username",
            "password": "New password",
            "data": "invalid json",
        },
    )

    assert response.status_code == 422


async def test_credential_encrypted_at_rest(
    session: AsyncSession, client: AsyncClient, monkeypatch
):
    monkeypatch.setattr(settings, "encryption_key", "test-key")

    response = await client.post(
        "/credentials/",
        json={
            "name": "Encrypted credential",
            "username": "Encrypted username",
            "password": "Encrypted password",
        },
    )
    assert response.status_code == 200
    credential_id = response.json()["id"]

    # The API returns decrypted values and reports the credential as encrypted
    response = await client.get(f"/credentials/{credential_id}")
    data = response.json()

    assert response.status_code == 200
    assert data["username"] == "Encrypted username"
    assert data["password"] == "Encrypted password"
    assert data["encrypted"] is True

    # The stored values are ciphertext
    row = (
        await session.execute(
            text("SELECT username, password FROM credential WHERE id = :id"),
            {"id": credential_id},
        )
    ).one()

    assert row[0].startswith("enc:v1:")
    assert row[1].startswith("enc:v1:")


async def test_credential_unencrypted_flag(
    session: AsyncSession, client: AsyncClient, monkeypatch
):
    monkeypatch.setattr(settings, "encryption_key", "set me in the env file")

    await generate_basic_data(session)

    response = await client.get("/credentials/")
    data = response.json()

    assert response.status_code == 200
    assert data[0]["encrypted"] is False

    response = await client.get("/credentials/1")
    assert response.json()["encrypted"] is False


async def test_credential_mixed_encryption_flags(
    session: AsyncSession, client: AsyncClient, monkeypatch
):
    # Existing credential saved without a key stays plaintext
    monkeypatch.setattr(settings, "encryption_key", "set me in the env file")
    await generate_basic_data(session)

    # New credential created after a key is configured is encrypted
    monkeypatch.setattr(settings, "encryption_key", "test-key")
    response = await client.post(
        "/credentials/",
        json={
            "name": "Encrypted credential",
            "username": "Encrypted username",
            "password": "Encrypted password",
        },
    )
    assert response.status_code == 200

    response = await client.get("/credentials/")
    flags = {c["name"]: c["encrypted"] for c in response.json()}

    assert flags["Secret credential"] is False
    assert flags["Encrypted credential"] is True


async def test_credential_encrypts_on_save_with_unchanged_values(
    session: AsyncSession, client: AsyncClient, monkeypatch
):
    # Credential created before a key was configured is stored as plaintext
    monkeypatch.setattr(settings, "encryption_key", "set me in the env file")
    await generate_basic_data(session)

    # Saving it unchanged after a key is configured must encrypt it
    monkeypatch.setattr(settings, "encryption_key", "test-key")
    response = await client.put(
        "/credentials/1",
        json={
            "name": "Secret credential",
            "username": "Secret username",
            "password": "My secret password",
        },
    )
    assert response.status_code == 200

    row = (
        await session.execute(
            text("SELECT username, password FROM credential WHERE id = 1")
        )
    ).one()

    assert row[0].startswith("enc:v1:")
    assert row[1].startswith("enc:v1:")

    response = await client.get("/credentials/1")
    data = response.json()
    assert data["username"] == "Secret username"
    assert data["password"] == "My secret password"
    assert data["encrypted"] is True


async def test_create_credential_with_empty_json_data(
    session: AsyncSession, client: AsyncClient
):
    response = await client.post(
        "/credentials/",
        json={
            "name": "New credential",
            "username": "New username",
            "password": "New password",
            "data": {},
        },
    )

    assert response.status_code == 200
