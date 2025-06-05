import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database.session import get_session
from app.main import app

from alembic import command
from alembic.config import Config
from app.config import settings

db_url = "postgresql://postgres:example@localhost:5432/ats_test"



@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(url=db_url)

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option('sqlalchemy.url', db_url)

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
