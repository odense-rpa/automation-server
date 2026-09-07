from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Base


async def test_models_match_migrations(session: AsyncSession):
    """Models must describe the schema the migrations actually build.

    When this fails, `alembic revision --autogenerate` would emit the listed
    operations — reverting hand-written schema features (indexes, unique
    constraints, FK actions, column types) that only exist because a
    hand-written migration added them and the model was never updated to
    match. Fix the model, not the migration.
    """
    conn = await session.connection()
    diff = await conn.run_sync(
        lambda sync_conn: compare_metadata(
            MigrationContext.configure(sync_conn), Base.metadata
        )
    )
    assert diff == [], f"models drifted from migrations: {diff}"
