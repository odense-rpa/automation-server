from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from app.database.unit_of_work import AbstractUnitOfWork
from app.database.models import WorkItem, AccessToken
from app.enums import WorkItemStatus

from .dependencies import get_unit_of_work, resolve_access_token
from .schemas import WorkItemUpdate, WorkItemStatusUpdate

router = APIRouter(prefix="/workitems", tags=["Workitems"])

# Dependency Injection local to this router

def get_workitem(
    item_id: int, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> WorkItem:
    with uow:
        workitem = uow.work_items.get(item_id)

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


@router.get("/{item_id}", responses=RESPONSE_STATES)
def get_workitem(
    workitem: WorkItem = Depends(get_workitem),
    token: AccessToken = Depends(resolve_access_token),
) -> WorkItem:
    return workitem


@router.put("/{item_id}", responses=RESPONSE_STATES)
def update_workitem(
    item: WorkItemUpdate,
    workitem: WorkItem = Depends(get_workitem),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> WorkItem:
    with uow:
        return uow.work_items.update(workitem, item.model_dump())


@router.put("/{item_id}/status", responses=RESPONSE_STATES)
def update_workitem_status(
    status: WorkItemStatusUpdate,
    workitem: WorkItem = Depends(get_workitem),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> WorkItem:
    with uow:
        data = status.model_dump()

        if status.status in [WorkItemStatus.COMPLETED, WorkItemStatus.FAILED]:
            data["locked"] = False

        return uow.work_items.update(workitem, data)
