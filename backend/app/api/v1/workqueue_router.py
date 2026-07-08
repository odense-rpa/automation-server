from fastapi import APIRouter, Depends, Query, Response
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError

import app.enums as enums
from app.api.v1.schemas import PaginatedResponse
from app.database.models import AccessToken, WorkItem, Workqueue
from app.database.unit_of_work import AbstractUnitOfWork
from app.services import WorkqueueService

from .dependencies import (
    get_paginated_search_params,
    get_unit_of_work,
    get_workqueue_service,
    resolve_access_token,
)
from .schemas import (
    PaginatedSearchParams,
    WorkItemCreate,
    WorkqueueClear,
    WorkqueueCreate,
    WorkqueueInformation,
    WorkqueueUpdate,
)

router = APIRouter(prefix="/workqueues", tags=["Workqueues"])


# Dependency Injection local to this router
async def get_workqueue(
    workqueue_id: int, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> Workqueue:
    async with uow:
        workqueue = await uow.workqueues.get(workqueue_id)

        if workqueue is None:
            raise HTTPException(status_code=404, detail="Workqueue not found")

        if workqueue.deleted:
            raise HTTPException(status_code=410, detail="Workqueue is gone")

        return workqueue


async def get_workqueue_by_name(
    workqueue_name: str, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> Workqueue:
    async with uow:
        workqueue = await uow.workqueues.get_by_name(workqueue_name)

        if workqueue is None:
            raise HTTPException(status_code=404, detail="Workqueue not found")

        if workqueue.deleted:
            raise HTTPException(status_code=410, detail="Workqueue is gone")

        return workqueue


@router.get("")
async def get_workqueues(
    include_deleted: bool = False,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> list[Workqueue]:
    async with uow:
        workqueues = await uow.workqueues.get_all(include_deleted)
        sorted_workqueues = sorted(workqueues, key=lambda wq: wq.name)

        return sorted_workqueues


@router.get("/information")
async def get_workqueues_information(
    include_deleted: bool = False,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> list[WorkqueueInformation]:
    async with uow:
        workqueues = await uow.workqueues.get_all(include_deleted)
        all_counts = await uow.workqueues.get_all_workitem_counts()

        result = []
        for queue in workqueues:
            counts = all_counts.get(queue.id, {})
            queue_info = WorkqueueInformation(
                id=queue.id,
                name=queue.name,
                description=queue.description,
                enabled=queue.enabled,
                auto_clean_max_age_days=queue.auto_clean_max_age_days,
                new=counts.get(enums.WorkItemStatus.NEW, 0),
                in_progress=counts.get(enums.WorkItemStatus.IN_PROGRESS, 0),
                completed=counts.get(enums.WorkItemStatus.COMPLETED, 0),
                failed=counts.get(enums.WorkItemStatus.FAILED, 0),
                pending_user_action=counts.get(
                    enums.WorkItemStatus.PENDING_USER_ACTION, 0
                ),
            )
            result.append(queue_info)

        return result


@router.get("/{workqueue_id}")
async def get_workqueue(
    workqueue: Workqueue = Depends(get_workqueue),
    token: AccessToken = Depends(resolve_access_token),
) -> Workqueue:
    return workqueue


@router.get("/by_name/{workqueue_name}")
async def get_workqueue_by_name(
    workqueue: Workqueue = Depends(get_workqueue_by_name),
    token: AccessToken = Depends(resolve_access_token),
) -> Workqueue:
    return workqueue


@router.put("/{workqueue_id}")
async def update_workqueue(
    update: WorkqueueUpdate,
    workqueue: Workqueue = Depends(get_workqueue),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> Workqueue:
    async with uow:
        return await uow.workqueues.update(workqueue, update.model_dump())


@router.post("")
async def create_workqueue(
    create: WorkqueueCreate,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> Workqueue:
    try:
        async with uow:
            return await uow.workqueues.create(create.model_dump())
    except IntegrityError:
        raise HTTPException(status_code=422, detail="Workqueue name already exists")


@router.delete("/{workqueue_id}", status_code=204)
async def delete_workqueue(
    workqueue: Workqueue = Depends(get_workqueue),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> None:
    async with uow:
        await uow.workqueues.delete(workqueue)
        return


@router.post("/{workqueue_id}/clear", status_code=204)
async def clear_workqueue(
    model: WorkqueueClear,
    workqueue: Workqueue = Depends(get_workqueue),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> Response:
    async with uow:
        await uow.workqueues.clear(
            workqueue.id, model.workitem_status, model.days_older_than
        )
        return


@router.post("/{workqueue_id}/add")
async def adds_workitem(
    item: WorkItemCreate,
    workqueue: Workqueue = Depends(get_workqueue),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> WorkItem:

    async with uow:
        # Force the initial state
        data = item.model_dump()
        data["workqueue_id"] = workqueue.id
        data["status"] = enums.WorkItemStatus.NEW
        data["locked"] = False
        data["deleted"] = False

        return await uow.work_items.create(data)


@router.get("/{workqueue_id}/next_item")
async def gets_next_workitem(
    workqueue: Workqueue = Depends(get_workqueue),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> WorkItem:

    if not workqueue.enabled:
        return Response(status_code=204)

    async with uow:
        item = await uow.work_items.get_next_item(workqueue.id)
        return item if item is not None else Response(status_code=204)


@router.get("/{workqueue_id}/items")
async def get_work_items(
    workqueue: Workqueue = Depends(get_workqueue),
    paginated_search: PaginatedSearchParams = Depends(get_paginated_search_params),
    service: WorkqueueService = Depends(get_workqueue_service),
    token: AccessToken = Depends(resolve_access_token),
) -> PaginatedResponse[WorkItem]:
    return await service.search_workitems(
        workqueue.id,
        paginated_search.pagination.page,
        paginated_search.pagination.size,
        paginated_search.search,
    )


@router.get("/{workqueue_id}/by_reference/{reference}")
async def get_workitems_by_reference_in_workqueue(
    reference: str,
    workqueue: Workqueue = Depends(get_workqueue),
    status: enums.WorkItemStatus | None = Query(
        None, description="Optional status filter"
    ),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> list[WorkItem]:
    async with uow:
        return await uow.workqueues.get_by_reference(workqueue.id, reference, status)
