from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from app.database.repository import WorkItemRepository
from app.database.models import WorkItem
from app.enums import WorkItemStatus

from .dependencies import get_repository
from .schemas import WorkItemUpdate, WorkItemStatusUpdate

router = APIRouter(prefix="/workitems", tags=["Workitems"])

@router.get("/{item_id}")
def get_workitem(item_id: int, repository: WorkItemRepository = Depends(get_repository(WorkItem))) -> WorkItem:
    item = repository.get(item_id)

    if item is None:
        raise HTTPException(status_code=404, detail="Workitem not found")

    return item

@router.put("/{item_id}")
def update_workitem(
    item_id: int, item: WorkItemUpdate, repository: WorkItemRepository = Depends(get_repository(WorkItem))
) -> WorkItem:
    workitem = repository.get(item_id)

    if workitem is None:
        raise HTTPException(status_code=404, detail="Workitem not found")
    
    return repository.update(workitem, item.model_dump())


@router.put("/{item_id}/status")
def update_workitem_status(
    item_id: int, status: WorkItemStatusUpdate, repository: WorkItemRepository = Depends(get_repository(WorkItem))
) -> WorkItem:
    workitem = repository.get(item_id)

    if workitem is None:
        raise HTTPException(status_code=404, detail="Workitem not found")

    data = status.model_dump()

    if status.status in [WorkItemStatus.COMPLETED, WorkItemStatus.FAILED]:
        data["locked"] = False

    return repository.update(workitem, data)

