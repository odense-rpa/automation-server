import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.workqueue import router as v1_workqueue_router
from app.api.v1.workitem import router as v1_workitem_router
from app.api.v1.process import router as v1_process_router
from app.api.v1.credentials import router as v1_credentials_router
from app.api.v1.resource import router as v1_resource_router
from app.api.v1.session import router as v1_session_router
from app.api.v1.trigger import router as v1_trigger_router
from app.api.v1.sessionlog import router as v1_sessionlog_router
from app.api.token import router as v1_access_token_router

from app.database.session import create_db_and_tables

from app.scheduler import schedule

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Automation server",
    description="Automation server",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_workqueue_router, prefix="/api")
app.include_router(v1_workitem_router, prefix="/api")
app.include_router(v1_process_router, prefix="/api")
app.include_router(v1_credentials_router, prefix="/api")
app.include_router(v1_resource_router, prefix="/api")
app.include_router(v1_session_router, prefix="/api")
app.include_router(v1_sessionlog_router, prefix="/api")
app.include_router(v1_trigger_router, prefix="/api")
app.include_router(v1_access_token_router, prefix="")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    asyncio.create_task(background_task())

async def background_task():
    while True:
        await asyncio.sleep(10)  # Sleep for 10 seconds        
        await schedule()
