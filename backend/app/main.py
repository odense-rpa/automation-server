import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.workqueue_router import router as v1_workqueue_router
from app.api.v1.workitem_router import router as v1_workitem_router
from app.api.v1.process_router import router as v1_process_router
from app.api.v1.credentials_router import router as v1_credentials_router
from app.api.v1.resource_router import router as v1_resource_router
from app.api.v1.session_router import router as v1_session_router
from app.api.v1.trigger_router import router as v1_trigger_router
from app.api.v1.sessionlog_router import router as v1_sessionlog_router
from app.api.v1.accesstoken_router import router as v1_accesstoken_router

from app.api.token_router import router as token_router

from app.database.session import create_db_and_tables
from app.config import settings
from app.scheduler import scheduler_background_task

logging.basicConfig(level=logging.INFO if settings.debug else logging.WARNING)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    
    # Create and store scheduler task reference to prevent garbage collection
    scheduler_task = asyncio.create_task(scheduler_background_task())
    
    logger.info(f"Starting up, database url is: {settings.database_url}, debug is {settings.debug}")

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
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    
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
app.include_router(v1_sessionlog_router, prefix="")
app.include_router(v1_trigger_router, prefix="")
app.include_router(v1_workitem_router, prefix="")
app.include_router(v1_workqueue_router, prefix="")
app.include_router(token_router, prefix="")


#async def background_task():
#    while True:
#        await asyncio.sleep(10)  # Sleep for 10 seconds
#        await schedule()
