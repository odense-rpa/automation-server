from datetime import datetime

from fastapi import APIRouter, Depends, Response
from fastapi.exceptions import HTTPException

from app.database.repository import (
    SessionRepository,
    ProcessRepository,
    ResourceRepository,
    SessionLogRepository,
)

from app.database.models import Session, Process, Resource, SessionLog
import app.enums as enums

from .schemas import (
    SessionCreate,
    SessionResourceUpdate,
    SessionStatusUpdate,
    SessionLogCreate,
)

from app.api.v1.schemas import PaginatedResponse, PaginatedSearchParams
from app.services import SessionService

from .dependencies import get_repository, get_session_service, get_paginated_search_params

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("")
def get_sessions(
    include_deleted: bool = False,
    paginated_search: PaginatedSearchParams = Depends(get_paginated_search_params),
    service: SessionService = Depends(get_session_service),
) -> PaginatedResponse[Session]:
    return service.search_sessions(paginated_search.pagination.page, paginated_search.pagination.size, paginated_search.search, include_deleted)


@router.get("/new")
def get_new_sessions(
    repository: SessionRepository = Depends(get_repository(Session)),
) -> list[Session]:
    return repository.get_new_sessions()


@router.get("/{session_id}")
def get_session(
    session_id: int,
    repository: SessionRepository = Depends(get_repository(Session)),
) -> Session:
    session = repository.get(session_id)

    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.deleted:
        raise HTTPException(status_code=403, detail="Session is deleted")

    return session

# The status update function handles the transition to from new to in_progress and to completed and failed
@router.put("/{session_id}/status")
def update_session_status(
    session_id: int,
    update: SessionStatusUpdate,
    repository: SessionRepository = Depends(get_repository(Session)),
    resource_repository: ResourceRepository = Depends(get_repository(Resource)),
) -> Session:
    session = repository.get(session_id)

    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.deleted:
        raise HTTPException(status_code=403, detail="Session is deleted")

    if not session.status.can_transition_to(update.status):
        raise HTTPException(status_code=400, detail="Invalid status transition")

    # There must be a resource assigned for a status update:
    if session.resource_id is None:
        raise HTTPException(
            status_code=400, detail="Resource must be assigned to update status"
        )

    # If the session is completed or failed, release the resource
    if update.status in [enums.SessionStatus.COMPLETED, enums.SessionStatus.FAILED]:
        resource = resource_repository.get(session.resource_id)
        resource_repository.update(resource, {"available": True})

    data = {"status": update.status}

    return repository.update(session, data)


@router.post("")
def create_session(
    session: SessionCreate,
    repository: SessionRepository = Depends(get_repository(Session)),
    process_repository: ProcessRepository = Depends(get_repository(Process)),
) -> Session:
    # Check if the process exists
    process = process_repository.get(session.process_id)
    if process is None:
        raise HTTPException(status_code=404, detail="Process not found")

    data = session.model_dump()
    data["deleted"] = False
    data["status"] = enums.SessionStatus.NEW
    data["dispatched_at"] = None
    data["created_at"] = datetime.now()
    data["updated_at"] = datetime.now()

    return repository.create(data)


@router.get("/by_resource_id/{resource_id}")
def get_active_sessions_by_resource(
    resource_id: int,
    repository: SessionRepository = Depends(get_repository(Session)),
    resource_repository: ResourceRepository = Depends(get_repository(Resource)),
) -> Session:
    
    resource = resource_repository.get(resource_id)
    
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    
    
    session = repository.get_by_resource_id(resource_id)

    if session is None:
        raise HTTPException(status_code=204, detail="No active sessions")

    return session


@router.post("/{session_id}/log")
def add_session_log(
    session_id: int,
    log: SessionLogCreate,
    session_repository: SessionRepository = Depends(get_repository(Session)),
    log_repository: SessionLogRepository = Depends(get_repository(SessionLog)),
) -> None:
    session = session_repository.get(session_id)

    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    data = log.model_dump()
    data["session_id"] = session_id
    data["created_at"] = datetime.now()

    log_repository.create(data)

    return Response(status_code=204)
