import os
import random
import time

import docker
import pytest
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from alembic import command
from app.config import settings
from app.database.session import get_session
from app.main import app


@pytest.fixture(scope="session")
def docker_postgresql_container():
    """Create PostgreSQL Docker container for testing session."""
    client = docker.from_env()

    port = random.randint(49152, 65535)  # Random port for Docker container

    # Container configuration
    container_config = {
        "image": "postgres:17",
        "environment": {
            "POSTGRES_DB": "postgres",
            "POSTGRES_USER": "test_user",
            "POSTGRES_PASSWORD": "test_password",
        },
        "ports": {"5432/tcp": port},  # Random port assignment
        "detach": True,
        "remove": True,  # Auto-remove when stopped
    }

    container = None
    try:
        # Start PostgreSQL container
        container = client.containers.run(**container_config)

        # Get the allocated port
        container.reload()

        # Wait for PostgreSQL to be ready
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                # Try to connect using psycopg2
                import psycopg2

                conn = psycopg2.connect(
                    host="localhost",
                    port=port,
                    database="postgres",
                    user="test_user",
                    password="test_password",
                )
                conn.close()
                break
            except psycopg2.OperationalError:
                if attempt == max_attempts - 1:
                    raise RuntimeError("PostgreSQL container failed to start")
                time.sleep(1)

        # Return connection details
        yield {
            "host": "localhost",
            "port": port,
            "database": "postgres",  # Initial database for container management
            "user": "test_user",
            "password": "test_password",
        }

    finally:
        # Cleanup container
        if container:
            try:
                container.stop()
            except Exception:
                pass


@pytest.fixture(name="session")
async def session_fixture(docker_postgresql_container):

    # Build the db URL for the test database
    container_info = docker_postgresql_container
    sync_url = f"postgresql://{container_info['user']}:{container_info['password']}@{container_info['host']}:{container_info['port']}/postgres"
    async_url = f"postgresql+asyncpg://{container_info['user']}:{container_info['password']}@{container_info['host']}:{container_info['port']}/postgres"

    settings.test_database_url = sync_url
    settings.database_url = sync_url
    os.environ["DATABASE_URL"] = sync_url

    # Use sync alembic for migrations (it uses psycopg2)
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", sync_url)

    # Apply all migrations to set up the database schema
    command.upgrade(alembic_cfg, "head")

    # Create async engine for tests
    engine = create_async_engine(url=async_url)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    await engine.dispose()
    command.downgrade(alembic_cfg, "base")


@pytest.fixture(name="client")
async def client_fixture(session: AsyncSession):
    async def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True
    ) as client:
        yield client

    app.dependency_overrides.clear()
