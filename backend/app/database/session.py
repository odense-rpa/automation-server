from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlmodel import create_engine

from app.config import settings


def _get_async_url(url: str) -> str:
    """Convert a sync postgresql:// URL to an async postgresql+asyncpg:// URL."""
    return url.replace("postgresql://", "postgresql+asyncpg://", 1)


# Async engine for the application
async_engine = create_async_engine(
    _get_async_url(settings.database_url),
    echo=False,
)

# Keep sync engine for Alembic migrations
sync_engine = create_engine(
    settings.database_url,
    echo=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(async_engine, expire_on_commit=False) as session:
        yield session
