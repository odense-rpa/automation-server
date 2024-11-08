from fastapi import APIRouter, Depends, Response
from fastapi.exceptions import HTTPException
from time import sleep

from sqlalchemy.exc import IntegrityError

from app.database.models import Workqueue, WorkItem, AccessToken
import app.enums as enums

from app.database.unit_of_work import AbstractUnitOfWork

from .schemas import (
    WorkqueueClear,
    WorkqueueUpdate,
    WorkqueueCreate,
    WorkItemCreate,
    WorkqueueInformation,
    PaginatedSearchParams,
)
from .dependencies import (
    get_unit_of_work,
    get_paginated_search_params,
    get_workqueue_service,
    resolve_access_token,
)

from app.api.v1.schemas import PaginatedResponse
from app.services import WorkqueueService

router = APIRouter(prefix="/workqueues", tags=["Workqueues"])


# Dependency Injection local to this router
def get_workqueue(
    workqueue_id: int, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> Workqueue:
    with uow:
        workqueue = uow.workqueues.get(workqueue_id)

        if workqueue is None:
            raise HTTPException(status_code=404, detail="Workqueue not found")

        if workqueue.deleted:
            raise HTTPException(status_code=410, detail="Workqueue is gone")

        return workqueue


@router.get("")
def get_workqueues(
    include_deleted: bool = False,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> list[Workqueue]:
    return uow.workqueues.get_all(include_deleted)


@router.get("/information")
def get_workqueues_information(
    include_deleted: bool = False,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> list[WorkqueueInformation]:
    with uow:
        workqueues = uow.workqueues.get_all(include_deleted)
        result = []
        for queue in workqueues:
            queue_info = WorkqueueInformation(
                id=queue.id,
                name=queue.name,
                description=queue.description,
                enabled=queue.enabled,
                new=uow.workqueues.get_workitem_count(
                    queue.id, enums.WorkItemStatus.NEW
                ),
                in_progress=uow.workqueues.get_workitem_count(
                    queue.id, enums.WorkItemStatus.IN_PROGRESS
                ),
                completed=uow.workqueues.get_workitem_count(
                    queue.id, enums.WorkItemStatus.COMPLETED
                ),
                failed=uow.workqueues.get_workitem_count(
                    queue.id, enums.WorkItemStatus.FAILED
                ),
                pending_user_action=uow.workqueues.get_workitem_count(
                    queue.id, enums.WorkItemStatus.PENDING_USER_ACTION
                ),
            )

            # Append to result
            result.append(queue_info)

        return result


@router.get("/{workqueue_id}")
def get_workqueue(
    workqueue: Workqueue = Depends(get_workqueue),
    token: AccessToken = Depends(resolve_access_token),
) -> Workqueue:
    return workqueue


@router.put("/{workqueue_id}")
def update_workqueue(
    update: WorkqueueUpdate,
    workqueue: Workqueue = Depends(get_workqueue),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> Workqueue:
    with uow:
        return uow.workqueues.update(workqueue, update.model_dump())


@router.post("")
def create_workqueue(
    create: WorkqueueCreate,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> Workqueue:
    with uow:
        return uow.workqueues.create(create.model_dump())


@router.delete("/{workqueue_id}", status_code=204)
def delete_workqueue(
    workqueue: Workqueue = Depends(get_workqueue),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> None:
    with uow:
        uow.workqueues.delete(workqueue)
        return


@router.post("/{workqueue_id}/clear", status_code=204)
def clear_workqueue(
    model: WorkqueueClear,
    workqueue: Workqueue = Depends(get_workqueue),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> Response:
    with uow:
        uow.workqueues.clear(workqueue.id, model.workitem_status, model.days_older_than)
        return


@router.post("/{workqueue_id}/add")
def adds_workitem(
    item: WorkItemCreate,
    workqueue: Workqueue = Depends(get_workqueue),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> WorkItem:

    with uow:
        # Force the initial state
        data = item.model_dump()
        data["workqueue_id"] = workqueue.id
        data["status"] = enums.WorkItemStatus.NEW
        data["locked"] = False
        data["deleted"] = False

        return uow.work_items.create(data)


@router.get("/{workqueue_id}/next_item")
def gets_next_workitem(
    workqueue: Workqueue = Depends(get_workqueue),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> WorkItem:
    
    if not workqueue.enabled:
        return Response(status_code=204)

    with uow:
        for retry_count in range(6):
            try:
                item = uow.work_items.get_next_item(workqueue.id)
                return item if item is not None else Response(status_code=204)
            except IntegrityError:
                if retry_count == 5:
                    return Response(
                        status_code=503, detail="Service is busy, please come back later"
                    )
                sleep(0.1)


@router.get("/{workqueue_id}/items")
def get_work_items(
    workqueue: Workqueue = Depends(get_workqueue),
    paginated_search: PaginatedSearchParams = Depends(get_paginated_search_params),
    service: WorkqueueService = Depends(get_workqueue_service),
    token: AccessToken = Depends(resolve_access_token),
) -> PaginatedResponse[WorkItem]:
    return service.search_workitems(
        workqueue.id,
        paginated_search.pagination.page,
        paginated_search.pagination.size,
        paginated_search.search,
    )
