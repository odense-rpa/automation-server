from typing import Generator
from sqlmodel import create_engine, Session

from alembic import command
from alembic.config import Config

from app.config import settings

connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    #echo=settings.debug is True,
    echo=False,
    #connect_args=connect_args,
)

def create_db_and_tables():
    # Configure Alembic to use the test database
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option('sqlalchemy.url', settings.database_url)

    # Apply all migrations to set up the database schema
    command.upgrade(alembic_cfg, "head")
    return 


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
