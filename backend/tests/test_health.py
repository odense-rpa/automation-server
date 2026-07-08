from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.main import app


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_health_ready_with_database(client: AsyncClient):
    response = await client.get("/health/ready")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


@pytest.mark.asyncio
async def test_health_ready_returns_503_when_database_down(session: AsyncSession):
    broken_session = AsyncMock(spec=AsyncSession)
    broken_session.execute.side_effect = ConnectionError("database unreachable")

    async def get_broken_session():
        yield broken_session

    app.dependency_overrides[get_session] = get_broken_session
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/health/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "unhealthy"
    assert data["database"].startswith("error:")
