import asyncio
import logging
from contextlib import asynccontextmanager
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as get_version

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.health_router import router as health_router
from app.api.token_router import router as token_router
from app.api.v1.accesstoken_router import router as v1_accesstoken_router
from app.api.v1.audit_log_router import router as v1_audit_log_router
from app.api.v1.credentials_router import router as v1_credentials_router
from app.api.v1.incident_router import router as v1_incident_router
from app.api.v1.process_router import router as v1_process_router
from app.api.v1.resource_router import router as v1_resource_router
from app.api.v1.session_router import router as v1_session_router
from app.api.v1.trigger_router import router as v1_trigger_router
from app.api.v1.workitem_router import router as v1_workitem_router
from app.api.v1.workqueue_router import router as v1_workqueue_router
from app.config import settings
from app.database import crypto
from app.database.crypto import EncryptionKeyError
from app.database.repository.credential_repository import CredentialRepository
from app.database.session import async_engine
from app.scheduler import scheduler_background_task

logging.basicConfig(level=logging.INFO if settings.debug else logging.WARNING)

logger = logging.getLogger(__name__)

try:
    APP_VERSION = get_version("automation_server_backend")
except PackageNotFoundError:
    APP_VERSION = "unknown"


async def warn_on_plaintext_credentials(session: AsyncSession | None = None) -> None:
    """Warn when credentials are, or still are, stored as plaintext.

    Logged at WARNING because production runs at that level (see
    logging.basicConfig above) — an INFO notice would be invisible in exactly
    the deployments that need it.

    Args:
        session: Session to check plaintext rows with. Defaults to a new
            session on the application engine.
    """
    if not crypto.is_configured():
        logger.warning(
            "ENCRYPTION_KEY is not set — credential usernames and passwords are "
            "stored as PLAINTEXT in the database. Set ENCRYPTION_KEY to encrypt "
            "them at rest; see docs/getting-started/configuration.md."
        )
        return

    # A key is configured, but rows written before it was set stay plaintext
    # until they are rewritten.
    try:
        if session is not None:
            unencrypted = await CredentialRepository(session).get_unencrypted_ids()
        else:
            async with AsyncSession(async_engine, expire_on_commit=False) as own:
                unencrypted = await CredentialRepository(own).get_unencrypted_ids()
    except Exception as e:  # noqa: BLE001 - never block startup on this check
        logger.warning(f"Could not check credential encryption status: {e}")
        return

    if unencrypted:
        logger.warning(
            f"{len(unencrypted)} credential(s) are still stored as PLAINTEXT from "
            "before ENCRYPTION_KEY was set. POST /credentials/reencrypt, or use "
            "'Encrypt all now' on the Credentials page, to rewrite them."
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create and store scheduler task reference to prevent garbage collection
    scheduler_task = asyncio.create_task(scheduler_background_task())

    logger.info(
        f"Starting up, database url is: {settings.database_url}, debug is {settings.debug}"
    )

    await warn_on_plaintext_credentials()

    try:
        yield
    finally:
        # Graceful shutdown: cancel scheduler task
        if scheduler_task and not scheduler_task.done():
            logger.info("Shutting down scheduler...")
            scheduler_task.cancel()
            try:
                await scheduler_task
            except asyncio.CancelledError:
                logger.info("Scheduler task cancelled successfully")
            except Exception as e:
                logger.error(f"Error during scheduler shutdown: {e}")


app = FastAPI(
    title="Automation server",
    description="Automation server",
    version=APP_VERSION,
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

@app.exception_handler(EncryptionKeyError)
async def encryption_key_error_handler(
    request: Request, exc: EncryptionKeyError
) -> JSONResponse:
    """Turn an unusable encryption key into an explanation, not a traceback.

    Without this, a changed or removed ENCRYPTION_KEY makes every credential
    read fail with a bare 500.
    """
    logger.error(f"Encryption key error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": (
                "Stored credentials cannot be decrypted with the configured "
                "ENCRYPTION_KEY. Restore the original key, or re-enter the "
                "affected credentials."
            )
        },
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_accesstoken_router, prefix="")
app.include_router(v1_credentials_router, prefix="")
app.include_router(v1_process_router, prefix="")
app.include_router(v1_resource_router, prefix="")
app.include_router(v1_session_router, prefix="")
app.include_router(v1_audit_log_router, prefix="")
app.include_router(v1_trigger_router, prefix="")
app.include_router(v1_workitem_router, prefix="")
app.include_router(v1_workqueue_router, prefix="")
app.include_router(v1_incident_router, prefix="")
app.include_router(token_router, prefix="")
app.include_router(health_router, prefix="")


# async def background_task():
#    while True:
#        await asyncio.sleep(10)  # Sleep for 10 seconds
#        await schedule()
