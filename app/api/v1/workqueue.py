from fastapi import APIRouter, Depends, Response
from fastapi.exceptions import HTTPException
from time import sleep

from sqlalchemy.exc import IntegrityError

from app.database.repository import WorkqueueRepository, WorkItemRepository
from app.database.models import Workqueue, WorkItem, AccessToken
import app.enums as enums

from .schemas import (
    WorkqueueUpdate,
    WorkItemCreate,
    WorkqueueInformation,
    PaginatedSearchParams,
)
from .dependencies import (
    get_repository,
    get_paginated_search_params,
    get_workqueue_service,
    resolve_access_token,
)

from app.api.v1.schemas import PaginatedResponse
from app.services import WorkqueueService

router = APIRouter(prefix="/workqueues", tags=["Workqueues"])


@router.get("")
def get_workqueues(
    include_deleted: bool = False,
    repository: WorkqueueRepository = Depends(get_repository(Workqueue)),
    token: AccessToken = Depends(resolve_access_token),
) -> list[Workqueue]:
    return repository.get_all(include_deleted)


@router.get("/information")
def get_workqueues_information(
    include_deleted: bool = False,
    repository: WorkqueueRepository = Depends(get_repository(Workqueue)),
    token: AccessToken = Depends(resolve_access_token),
) -> list[WorkqueueInformation]:
    workqueues = repository.get_all(include_deleted)
    result = []
    for queue in workqueues:
        queue_info = WorkqueueInformation(
            id=queue.id,
            name=queue.name,
            description=queue.description,
            enabled=queue.enabled,
            new=repository.get_workitem_count(queue.id, enums.WorkItemStatus.NEW),
            in_progress=repository.get_workitem_count(
                queue.id, enums.WorkItemStatus.IN_PROGRESS
            ),
            completed=repository.get_workitem_count(
                queue.id, enums.WorkItemStatus.COMPLETED
            ),
            failed=repository.get_workitem_count(queue.id, enums.WorkItemStatus.FAILED),
            pending_user_action=repository.get_workitem_count(
                queue.id, enums.WorkItemStatus.PENDING_USER_ACTION
            ),
        )

        # Append to result
        result.append(queue_info)

    return result


@router.get("/{workqueue_id}")
def get_workqueue(
    workqueue_id: str,
    repository: WorkqueueRepository = Depends(get_repository(Workqueue)),
    token: AccessToken = Depends(resolve_access_token),
) -> Workqueue:
    workqueue = repository.get(workqueue_id)

    if workqueue is None:
        raise HTTPException(status_code=404, detail="Workqueue not found")

    if workqueue.deleted:
        raise HTTPException(status_code=403, detail="Workqueue is deleted")

    return workqueue


@router.put("/{workqueue_id}")
def update_workqueue(
    workqueue_id: str,
    update: WorkqueueUpdate,
    repository: WorkqueueRepository = Depends(get_repository(Workqueue)),
    token: AccessToken = Depends(resolve_access_token),
) -> Workqueue:
    workqueue = repository.get(workqueue_id)

    if workqueue is None:
        raise HTTPException(status_code=404, detail="Workqueue not found")

    if workqueue.deleted:
        raise HTTPException(status_code=403, detail="Workqueue is deleted")

    return repository.update(workqueue, update.model_dump())


@router.post("")
def create_workqueue(
    workqueue: Workqueue,
    repository: WorkqueueRepository = Depends(get_repository(Workqueue)),
    token: AccessToken = Depends(resolve_access_token),
) -> Workqueue:
    return repository.create(workqueue.model_dump())


@router.delete("/{workqueue_id}")
def delete_workqueue(
    workqueue_id: str,
    repository: WorkqueueRepository = Depends(get_repository(Workqueue)),
    token: AccessToken = Depends(resolve_access_token),
) -> dict:
    workqueue = repository.get(workqueue_id)

    if workqueue is None:
        raise HTTPException(status_code=404, detail="Workqueue not found")

    if workqueue.deleted:
        raise HTTPException(status_code=403, detail="Workqueue is deleted")

    return repository.delete(workqueue)


@router.post("/{queue_id}/add")
def adds_workitem(
    queue_id: str,
    item: WorkItemCreate,
    repository: WorkqueueRepository = Depends(get_repository(Workqueue)),
    item_repository: WorkItemRepository = Depends(get_repository(WorkItem)),
    token: AccessToken = Depends(resolve_access_token),
) -> WorkItem:
    queue = repository.get(queue_id)
    if queue is None:
        raise HTTPException(status_code=404, detail="Queue not found")

    # Force the initial state
    data = item.model_dump()
    data["workqueue_id"] = queue_id
    data["status"] = enums.WorkItemStatus.NEW
    data["locked"] = False
    data["deleted"] = False

    return item_repository.create(data)


@router.get("/{queue_id}/next_item")
def gets_next_workitem(
    queue_id: str,
    repository: WorkqueueRepository = Depends(get_repository(Workqueue)),
    item_repository: WorkItemRepository = Depends(get_repository(WorkItem)),
    token: AccessToken = Depends(resolve_access_token),
) -> WorkItem:
    queue = repository.get(queue_id)

    if queue is None:
        raise HTTPException(status_code=404, detail="Queue not found")

    for retry_count in range(6):
        try:
            item = item_repository.get_next_item(queue_id)
            return item if item is not None else Response(status_code=204)
        except IntegrityError:
            if retry_count == 5:
                return Response(
                    status_code=503, detail="Service is busy, please come back later"
                )
            sleep(0.1)


@router.get("/{queue_id}/items")
def get_work_items(
    queue_id: str,
    paginated_search: PaginatedSearchParams = Depends(get_paginated_search_params),
    repository: WorkqueueRepository = Depends(get_repository(Workqueue)),
    service: WorkqueueService = Depends(get_workqueue_service),
    token: AccessToken = Depends(resolve_access_token),
) -> PaginatedResponse[WorkItem]:
    queue = repository.get(queue_id)

    if queue is None:
        raise HTTPException(status_code=404, detail="Queue not found")

    return service.search_workitems(
        queue_id,
        paginated_search.pagination.page,
        paginated_search.pagination.size,
        paginated_search.search,
    )
