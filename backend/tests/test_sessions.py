from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from . import generate_basic_data  # noqa: F401

async def test_get_session_logs(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/audit-logs/525")
    assert response.status_code == 404


    response = await client.get("/audit-logs/1")
    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["total_items"] == 2
    assert data["total_pages"] == 1

    response = await client.get("/audit-logs/1?size=1")
    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["total_items"] == 2
    assert data["total_pages"] == 2


async def test_get_sessionlog_by_workitem(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    response = await client.get("/audit-logs/by_workitem/525")
    assert response.status_code == 404

    response = await client.get("/audit-logs/by_workitem/1")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
