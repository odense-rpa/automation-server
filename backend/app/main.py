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


async def check_credential_encryption(session: AsyncSession | None = None) -> None:
    """Report credential encryption problems at startup.

    Logged at WARNING and above because production runs at that level (see
    logging.basicConfig), so an INFO notice would be invisible in exactly the
    deployments that need it.

    Args:
        session: Session to inspect stored credentials with. Defaults to a
            new session on the application engine.
    """
    key_configured = crypto.is_configured()

    if not key_configured:
        logger.warning(
            "ENCRYPTION_KEY is not set — credential usernames and passwords are "
            "stored as PLAINTEXT in the database. Set ENCRYPTION_KEY to encrypt "
            "them at rest; see docs/getting-started/configuration.md."
        )

    try:
        if session is not None:
            await _report_credential_encryption(session, key_configured)
        else:
            async with AsyncSession(async_engine, expire_on_commit=False) as own:
                await _report_credential_encryption(own, key_configured)
    except Exception as e:  # noqa: BLE001 - never block startup on this check
        logger.warning(f"Could not check credential encryption status: {e}")


async def _report_credential_encryption(
    session: AsyncSession, key_configured: bool
) -> None:
    repository = CredentialRepository(session)

    if not key_configured:
        # The damaging case: a key was configured once, credentials were
        # encrypted with it, and it has since been removed. Those values are
        # unreadable until it comes back.
        encrypted = await repository.get_encrypted_ids()
        if encrypted:
            logger.error(
                f"{len(encrypted)} credential(s) are encrypted but ENCRYPTION_KEY "
                "is not set — they CANNOT be read and every credential request "
                "will fail. Restore the ENCRYPTION_KEY value this server was "
                "previously started with, or delete and re-enter these credentials."
            )
        return

    if not await repository.can_decrypt():
        logger.error(
            "Stored credentials are encrypted with a different key than the "
            "configured ENCRYPTION_KEY — they CANNOT be read and every credential "
            "request will fail. Restore the previous ENCRYPTION_KEY value, or "
            "delete and re-enter the affected credentials."
        )
        return

    unencrypted = await repository.get_unencrypted_ids()
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

    await check_credential_encryption()

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
    read fail with a bare 500 that says nothing about the cause.
    """
    logger.error(f"Encryption key error on {request.url.path}: {exc}")

    if crypto.is_configured():
        detail = (
            "These credentials are encrypted with a different key than the "
            "ENCRYPTION_KEY this server is configured with, so they cannot be "
            "read. Restore the previous ENCRYPTION_KEY value and restart the "
            "server, or delete and re-enter the affected credentials."
        )
    else:
        detail = (
            "These credentials are encrypted, but no ENCRYPTION_KEY is "
            "configured on the server, so they cannot be read. Restore the "
            "ENCRYPTION_KEY value the server was previously started with, or "
            "delete and re-enter the affected credentials."
        )

    return JSONResponse(status_code=500, content={"detail": detail})


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
