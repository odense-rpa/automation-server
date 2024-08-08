from datetime import datetime

from fastapi import APIRouter, Depends, Response
from fastapi.exceptions import HTTPException

from app.database.repository import (
    SessionRepository,
    ProcessRepository,
    ResourceRepository,
    SessionLogRepository,
    WorkItemRepository,

)

from app.api.v1.schemas import PaginatedSearchParams

from app.database.models import SessionLog, WorkItem, Session
from app.services import SessionLogService
import app.enums as enums

from app.api.v1.schemas import PaginatedResponse

from .dependencies import get_repository, get_paginated_search_params, get_sessionlog_service

router = APIRouter(prefix="/sessionlogs", tags=["Sessionlogs"])


@router.get("/{session_id}")
def get_sessionlogs(
    session_id: int,
    paginated_search: PaginatedSearchParams = Depends(get_paginated_search_params),
    service: SessionLogService = Depends(get_sessionlog_service),
    repository: SessionRepository = Depends(get_repository(Session)),
) -> PaginatedResponse[SessionLog]:

    # Check for session
    session = repository.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return service.search_logs(session_id, paginated_search.pagination.page, paginated_search.pagination.size, paginated_search.search)

@router.get("/by_workitem/{workitem_id}")
def get_by_workitem(
    workitem_id: int,
    service: SessionLogService = Depends(get_sessionlog_service),
    repository: WorkItemRepository = Depends(get_repository(WorkItem)),
) -> list[SessionLog]:
    
    # Check for session
    item = repository.get(workitem_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Workitem not found")
   
    return service.get_by_workitem(workitem_id)