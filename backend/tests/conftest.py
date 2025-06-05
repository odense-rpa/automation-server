import pytest

from alembic import command
from alembic.config import Config

from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine


from app.main import app
from app.config import settings
from app.database.session import get_session


@pytest.fixture(name="session")
def session_fixture():
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
