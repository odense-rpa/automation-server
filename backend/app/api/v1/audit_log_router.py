from fastapi import APIRouter, Depends

from app.api.v1.schemas import PaginatedSearchParams, AuditLogCreate

from app.database.models import AuditLog, WorkItem, Session, AccessToken
from app.database.unit_of_work import AbstractUnitOfWork

from app.services import AuditLogService

from . import error_descriptions

from app.api.v1.schemas import PaginatedResponse

from .dependencies import (
    get_paginated_search_params,
    get_auditlog_service,
    resolve_access_token,
    get_unit_of_work,
)

from .session_router import (
    get_session as get_session_dependency,
)

from .workitem_router import (
    get_workitem as get_workitem_dependency,
)

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.post("", status_code=204)
def create_log(
    log: AuditLogCreate,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> None:
    with uow:
        
        uow.auditlogs.create(log.model_dump())
        uow.commit()


@router.get("/{session_id}", responses=error_descriptions("Session", _403=True, _404=True))
def get_auditlogs(
    paginated_search: PaginatedSearchParams = Depends(get_paginated_search_params),
    session: Session = Depends(get_session_dependency),
    service: AuditLogService = Depends(get_auditlog_service),
    token: AccessToken = Depends(resolve_access_token),
) -> PaginatedResponse[AuditLog]:
    return service.search_logs(
        session.id,
        paginated_search.pagination.page,
        paginated_search.pagination.size,
        paginated_search.search,
    )


@router.get("/by_workitem/{item_id}", responses=error_descriptions("WorkItem", _403=True, _404=True, _410=True))
def get_by_workitem(
    workitem: WorkItem = Depends(get_workitem_dependency),
    service: AuditLogService = Depends(get_auditlog_service),
    token: AccessToken = Depends(resolve_access_token),
) -> list[AuditLog]:
    return service.get_by_workitem(workitem.id)