from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException

from app.database.models import Incident, AccessToken
from app.database.unit_of_work import AbstractUnitOfWork
from app.enums import IncidentStatus
from app.services import IncidentService

from .schemas import IncidentResolve, PaginatedResponse
from .dependencies import (
    get_unit_of_work,
    get_incident_service,
    resolve_access_token,
)
from . import error_descriptions

router = APIRouter(prefix="/incidents", tags=["Incidents"])


async def get_incident_dependency(
    incident_id: int, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> Incident:
    async with uow:
        incident = await uow.incidents.get(incident_id)

        if incident is None:
            raise HTTPException(status_code=404, detail="Incident not found")

        if incident.deleted:
            raise HTTPException(status_code=410, detail="Incident is gone")

        return incident


@router.get("", responses=error_descriptions("Incident", _403=True))
async def list_incidents(
    status: Optional[IncidentStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None, description="Search by process name"),
    service: IncidentService = Depends(get_incident_service),
    token: AccessToken = Depends(resolve_access_token),
) -> PaginatedResponse[Incident]:
    return await service.search_incidents(page, size, search, status)


@router.get("/open", responses=error_descriptions("Incident", _403=True))
async def list_open_incidents(
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> list[Incident]:
    async with uow:
        return await uow.incidents.get_open_incidents()


@router.get("/open/count", responses=error_descriptions("Incident", _403=True))
async def count_open_incidents(
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> dict:
    async with uow:
        return {"count": await uow.incidents.count_open_incidents()}


@router.post("/dismiss-all", responses=error_descriptions("Incident", _403=True))
async def dismiss_all_incidents(
    service: IncidentService = Depends(get_incident_service),
    token: AccessToken = Depends(resolve_access_token),
) -> dict:
    count = await service.dismiss_all_open()
    return {"dismissed": count}


@router.get(
    "/{incident_id}",
    responses=error_descriptions("Incident", _403=True, _404=True, _410=True),
)
async def get_incident(
    incident: Incident = Depends(get_incident_dependency),
    token: AccessToken = Depends(resolve_access_token),
) -> Incident:
    return incident


@router.put(
    "/{incident_id}/resolve",
    responses={
        400: {
            "description": "Invalid status transition",
            "content": {
                "application/json": {"example": {"detail": "Invalid status transition"}}
            },
        }
    }
    | error_descriptions("Incident", _403=True, _404=True, _410=True),
)
async def resolve_incident(
    resolve: IncidentResolve,
    incident: Incident = Depends(get_incident_dependency),
    service: IncidentService = Depends(get_incident_service),
    token: AccessToken = Depends(resolve_access_token),
) -> Incident:
    try:
        return await service.resolve_incident(
            incident, resolve.status, resolve.resolution_note
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{incident_id}",
    responses=error_descriptions("Incident", _403=True, _404=True, _410=True),
)
async def delete_incident(
    incident: Incident = Depends(get_incident_dependency),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> Incident:
    async with uow:
        db_incident = await uow.incidents.get(incident.id)
        if db_incident is None:
            raise HTTPException(status_code=404, detail="Incident not found")
        return await uow.incidents.delete(db_incident)
