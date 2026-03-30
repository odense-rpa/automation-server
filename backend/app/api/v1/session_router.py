from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException


from app.database.unit_of_work import AbstractUnitOfWork

from app.database.models import Session, Process, Resource, AccessToken
import app.enums as enums

from .schemas import (
    SessionCreate,
    SessionStatusUpdate,
    ProcessActivitySummary,
)

from app.api.v1.schemas import PaginatedResponse, PaginatedSearchParams
from app.services import SessionService

from .dependencies import (
    get_unit_of_work,
    get_session_service,
    get_incident_service,
    get_paginated_search_params,
    resolve_access_token,
)
from app.services import IncidentService

from . import error_descriptions

# We borrow the get_resource function from the resource_router module to check for a valid resource
from .resource_router import get_resource

router = APIRouter(prefix="/sessions", tags=["Sessions"])

# Dependency Injection local to this router


async def get_session(
    session_id: int, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> Process:
    async with uow:
        session = await uow.sessions.get(session_id)

        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")

        if session.deleted:
            raise HTTPException(status_code=410, detail="Session is gone")

        return session


# Error responses


@router.get("", responses=error_descriptions("Session", _403=True))
async def get_sessions(
    include_deleted: bool = False,
    paginated_search: PaginatedSearchParams = Depends(get_paginated_search_params),
    service: SessionService = Depends(get_session_service),
    token: AccessToken = Depends(resolve_access_token),
) -> PaginatedResponse[Session]:
    return await service.search_sessions(
        paginated_search.pagination.page,
        paginated_search.pagination.size,
        paginated_search.search,
        include_deleted,
    )


@router.get("/new", responses=error_descriptions("Session", _403=True))
async def get_new_sessions(
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> list[Session]:
    return await uow.sessions.get_new_sessions()


@router.get("/activity-summary", responses=error_descriptions("Session", _403=True))
async def get_activity_summary(
    hours: int = 24,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> list[ProcessActivitySummary]:
    since = datetime.now() - timedelta(hours=hours)
    async with uow:
        return await uow.sessions.get_process_activity_summary(since)


@router.get(
    "/{session_id}",
    responses=error_descriptions("Session", _403=True, _404=True, _410=True),
)
async def get_session(
    session: Session = Depends(get_session),
    token: AccessToken = Depends(resolve_access_token),
) -> Session:
    return session


# The status update function handles the transition to from new to in_progress and to completed and failed
@router.put(
    "/{session_id}/status",
    responses={
        400: {
            "description": "Invalid status transition or resource not assigned",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid status transition or resource not assigned"
                    }
                }
            },
        }
    }
    | error_descriptions("Session", _403=True),
)
async def update_session_status(
    update: SessionStatusUpdate,
    session: Session = Depends(get_session),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    incident_service: IncidentService = Depends(get_incident_service),
    token: AccessToken = Depends(resolve_access_token),
) -> Session:
    if not session.status.can_transition_to(update.status):
        raise HTTPException(status_code=400, detail="Invalid status transition")

    # There must be a resource assigned for a status update:
    if session.resource_id is None:
        raise HTTPException(
            status_code=400, detail="Resource must be assigned to update status"
        )

    async with uow:
        # If the session is completed or failed, release the resource
        if update.status in [enums.SessionStatus.COMPLETED, enums.SessionStatus.FAILED]:
            resource = await uow.resources.get(session.resource_id)
            await uow.resources.update(resource, {"available": True})

        data = {"status": update.status}

        updated_session = await uow.sessions.update(session, data)

        if update.status == enums.SessionStatus.FAILED:
            await incident_service.create_incident_for_session(updated_session)

        return updated_session


@router.post(
    "",
    responses=error_descriptions("Process", _403=True, _404=True),
)
async def create_session(
    session: SessionCreate,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> Session:
    async with uow:
        # Check if the process exists
        process = await uow.processes.get(session.process_id)
        if process is None:
            raise HTTPException(status_code=404, detail="Process not found")

        data = session.model_dump()
        data["deleted"] = False
        data["status"] = enums.SessionStatus.NEW
        data["dispatched_at"] = None
        data["created_at"] = datetime.now()
        data["updated_at"] = datetime.now()

        return await uow.sessions.create(data)


@router.get(
    "/by_resource_id/{resource_id}",
    responses=error_descriptions("Session", _403=True, _204=True)
    | error_descriptions("Resource", _404=True),
)
async def get_active_sessions_by_resource(
    resource: Resource = Depends(get_resource),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> Session:
    async with uow:
        session = await uow.sessions.get_by_resource_id(resource.id)

        if session is None:
            raise HTTPException(status_code=204, detail="No active sessions")

        return session
