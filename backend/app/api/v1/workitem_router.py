from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException

from app.database.models import AccessToken, WorkItem
from app.database.unit_of_work import AbstractUnitOfWork
from app.enums import WorkItemStatus

from .dependencies import get_unit_of_work, resolve_access_token
from .schemas import WorkItemRead, WorkItemStatusUpdate, WorkItemUpdate

router = APIRouter(prefix="/workitems", tags=["Workitems"])

# Dependency Injection local to this router


async def get_workitem(
    item_id: int, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> WorkItem:
    async with uow:
        workitem = await uow.work_items.get(item_id)

        if workitem is None:
            raise HTTPException(status_code=404, detail="Workitem not found")

        return workitem


# Error responses

RESPONSE_STATES = {
    404: {
        "description": "Workitem not found",
        "content": {"application/json": {"example": {"detail": "Workitem not found"}}},
    }
}


@router.get("/{item_id}", responses=RESPONSE_STATES, response_model=WorkItemRead)
async def get_workitem(
    workitem: WorkItem = Depends(get_workitem),
    token: AccessToken = Depends(resolve_access_token),
) -> WorkItem:
    return workitem


@router.put("/{item_id}", responses=RESPONSE_STATES, response_model=WorkItemRead)
async def update_workitem(
    item: WorkItemUpdate,
    workitem: WorkItem = Depends(get_workitem),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> WorkItem:
    async with uow:
        update_data = item.model_dump(exclude_unset=True)
        # Filter out None values for non-nullable fields
        if update_data.get("data") is None:
            update_data.pop("data", None)
        return await uow.work_items.update(workitem, update_data)


@router.put("/{item_id}/status", responses=RESPONSE_STATES, response_model=WorkItemRead)
async def update_workitem_status(
    status: WorkItemStatusUpdate,
    workitem: WorkItem = Depends(get_workitem),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> WorkItem:
    async with uow:
        data = status.model_dump(exclude_unset=True)

        # Always set started_at when status is IN_PROGRESS
        if status.status == WorkItemStatus.IN_PROGRESS:
            data["started_at"] = datetime.now()

        # Calculate work duration for terminal statuses if started_at is set
        if workitem.started_at and status.status in [
            WorkItemStatus.COMPLETED,
            WorkItemStatus.FAILED,
        ]:
            duration = (datetime.now() - workitem.started_at).total_seconds()
            data["work_duration_seconds"] = int(duration)

        # We clear the locked flag because these statuses indicate that we have stopped working on the item
        if status.status in [
            WorkItemStatus.COMPLETED,
            WorkItemStatus.FAILED,
            WorkItemStatus.NEW,
            WorkItemStatus.PENDING_USER_ACTION,
        ]:
            data["locked"] = False

        return await uow.work_items.update(workitem, data)


@router.get("/by-reference/{reference}", response_model=list[WorkItemRead])
async def get_workitems_by_reference(
    reference: str,
    status: WorkItemStatus | None = Query(None, description="Optional status filter"),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> list[WorkItem]:
    async with uow:
        return await uow.work_items.get_by_reference(reference, status)
