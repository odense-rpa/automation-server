import pytest
import docker
import random
import time
import os
from alembic import command
from alembic.config import Config

from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine


from app.main import app
from app.config import settings
from app.database.session import get_session

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
                    password="test_password"
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
def session_fixture(docker_postgresql_container):

    # Build the db URL for the test database
    container_info = docker_postgresql_container
    settings.test_database_url = f"postgresql://{container_info['user']}:{container_info['password']}@{container_info['host']}:{container_info['port']}/postgres"


    engine = create_engine(url=settings.test_database_url)

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.test_database_url)

    # Apply all migrations to set up the database schema
    command.upgrade(alembic_cfg, "head")

    with Session(engine) as session:
        yield session

    command.downgrade(alembic_cfg, "base")


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
