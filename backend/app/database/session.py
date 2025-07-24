from typing import Generator
from sqlmodel import create_engine, Session


from app.config import settings

connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    #echo=settings.debug is True,
    echo=False,
    #connect_args=connect_args,
)



def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
