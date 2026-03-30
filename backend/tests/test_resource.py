from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from . import generate_basic_data  # noqa: F401


async def test_get_resources(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/resources")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2

    assert data[0]["name"] == "resource"
    assert data[0]["fqdn"] == "resource.example.com"
    assert data[0]["deleted"] is False

    response = await client.get("/resources/?include_deleted=true")
    data = response.json()
    assert len(data) == 4


async def test_get_resource(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/resources/1")
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "resource"
    assert data["fqdn"] == "resource.example.com"
    assert data["deleted"] is False


async def test_create_resource(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.post(
        "/resources",
        json={
            "name": "resource3",
            "fqdn": "resource3.example.com",
            "capabilities": "win32 chrome blueprism",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "resource3"
    assert data["fqdn"] == "resource3.example.com"
    assert data["available"] is True
    assert data["last_seen"] is not None


async def test_resource_should_expire(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/resources/3")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "resource-should-expire"
    assert data["available"] is True
    assert data["deleted"] is False

    # This will trigger a full available resource update
    response = await client.get("/resources")
    assert response.status_code == 200

    response = await client.get("/resources/3")
    assert response.status_code == 404


async def test_update_resource(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.put(
        "/resources/1",
        json={
            "name": "resource",
            "fqdn": "resource.example.com",
            "capabilities": "win32 chrome python",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "resource"
    assert data["fqdn"] == "resource.example.com"
    assert data["capabilities"] == "win32 chrome python"
    assert data["available"] is True
    assert data["last_seen"] is not None


async def test_update_resource_preserve_available(
    session: AsyncSession, client: AsyncClient
):
    await generate_basic_data(session)

    response = await client.put(
        "/resources/4",
        json={
            "name": "resource-not-available",
            "fqdn": "resource-not-available.example.com",
            "capabilities": "win32 chrome python",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "resource-not-available"
    assert data["fqdn"] == "resource-not-available.example.com"
    assert data["capabilities"] == "win32 chrome python"
    assert data["available"] is False
    assert data["last_seen"] is not None


async def test_update_old_resource(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.put(
        "/resources/2",
        json={
            "name": "resource-old",
            "fqdn": "resource-old.example.com",
            "capabilities": "win32 chrome python blue_prism",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "resource-old"
    assert data["fqdn"] == "resource-old.example.com"
    assert data["capabilities"] == "win32 chrome python blue_prism"
    assert data["available"] is True
    assert data["last_seen"] is not None
