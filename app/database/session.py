from typing import Generator
from sqlmodel import create_engine, SQLModel, Session

# from core.config import config, EnvironmentType

from app.config import settings

connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    #echo=settings.debug is True,
    echo=False,
    connect_args=connect_args,
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
