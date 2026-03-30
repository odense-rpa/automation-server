from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import app.database.models as models

from . import generate_basic_data  # noqa: F401


async def test_get_processes(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/processes/")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["name"] == "Process"
    assert data[0]["description"] == "Process for unittest"
    assert data[0]["deleted"] is False

    response = await client.get("/processes/?include_deleted=true")
    data = response.json()
    assert len(data) == 2


async def test_get_process(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/processes/1")

    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Process"
    assert data["description"] == "Process for unittest"
    assert data["deleted"] is False

    response = await client.get("/processes/2")

    assert response.status_code == 410

async def test_update_process(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.put(
        "/processes/1",
        json={
            "name": "Process",
            "description": "New description",
            "workqueue_id": 1,
            "target_type": "python",
            "target_source": "Test url",
            "target_credentials_id": 1,
            "credentials_id": 1
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Process"
    assert data["description"] == "New description"

    data = await session.get(models.Process, 1)

    assert data.name == "Process"
    assert data.description == "New description"
    assert data.workqueue_id == 1
    assert data.target_type == "python"
    assert data.target_source == "Test url"
    assert data.target_credentials_id == 1
    assert data.credentials_id == 1

async def test_create_process(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.post(
        "/processes/",
        json={
            "name": "Process",
            "description": "New description",
            "workqueue_id": 1,
            "target_type": "python",
            "target_source": "Test url",
            "target_credentials_id": None,
            "credentials_id": None
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Process"
    assert data["description"] == "New description"


async def test_delete_process(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.delete("/processes/1")

    assert response.status_code == 204

    process = await session.get(models.Process, 1)
    assert process.deleted is True

    response = await client.get("/processes/1")
    assert response.status_code == 410

async def test_create_trigger_on_process(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.post(
        "/processes/1/trigger",
        json={
            "type": "cron",
            "cron": "15 4 * * *",
            "enabled": False,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["type"] == "cron"
    assert data["cron"] == "15 4 * * *"
    assert data["enabled"] is False

async def test_get_triggers_on_process(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.post(
        "/processes/1/trigger",
        json={
            "type": "cron",
            "cron": "15 4 * * *",
            "enabled": False,
        },
    )

    response = await client.get("/processes/1/trigger")

    assert response.status_code == 200

    # 3 triggers are created in generate_basic_data and we want number 4
    data = response.json()
    assert data[3]["type"] == "cron"
    assert data[3]["cron"] == "15 4 * * *"
    assert data[3]["enabled"] is False
