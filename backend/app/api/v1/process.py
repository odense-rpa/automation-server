from fastapi import APIRouter, Depends, Response
from fastapi.exceptions import HTTPException

from app.database.repository import ProcessRepository, TriggerRepository
from app.database.models import Process, Trigger, AccessToken

from .schemas import ProcessCreate, ProcessUpdate, TriggerCreate
from .dependencies import get_repository, resolve_access_token, get_unit_of_work

import app.enums as enums

from app.database.unit_of_work import AbstractUnitOfWork

router = APIRouter(prefix="/processes", tags=["Processes"])


# Dependency Injection
def get_process(
    process_id: int, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> Process:
    with uow:
        process = uow.processes.get(process_id)

        if process is None:
            raise HTTPException(status_code=404, detail="Process not found")

        if process.deleted:
            raise HTTPException(status_code=410, detail="Process is gone")

        return process


# Error response
RESPONSE_STATES = {
    404: {
        "description": "Item not found",
        "content": {"application/json": {"example": {"detail": "Process not found"}}},
    },
    410: {
        "description": "Process is gone",
        "content": {"application/json": {"example": {"detail": "Process is gone"}}},
    },
}


# Routes
@router.get("")
def get_processes(
    include_deleted: bool = False,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> list[Process]:
    with uow:
        return uow.processes.get_all(include_deleted)


@router.get("/{process_id}")
def get_process(
    process: Process = Depends(get_process),
    token: AccessToken = Depends(resolve_access_token),
) -> Process:
    return process


@router.put("/{process_id}")
def update_process(
    update: ProcessUpdate,
    process: Process = Depends(get_process),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> Process:
    with uow:
        return uow.processes.update(process, update.model_dump())


@router.post("")
def create_process(
    process: ProcessCreate,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> Process:
    with uow:
        data = process.model_dump()
        data["deleted"] = False

        return uow.processes.create(data)


@router.delete(
    "/{process_id}",
    status_code=204,
    responses={
        204: {
            "description": "Item deleted",
            "content": {"application/json": {"example": {"detail": "Process has been deleted"}}},
        }
    }
    | RESPONSE_STATES,
)
def delete_process(
    process: Process = Depends(get_process),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> None:
    with uow:
        uow.processes.delete(process)
        return 


@router.post("/{process_id}/trigger")
def create_trigger(
    process_id: int,
    trigger: TriggerCreate,
    process: Process = Depends(get_process),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),

    repository: TriggerRepository = Depends(get_repository(Trigger)),
    #process_repository: ProcessRepository = Depends(get_repository(Process)),
    token: AccessToken = Depends(resolve_access_token),
) -> Trigger:
    data = trigger.model_dump()
    data["deleted"] = False

    with uow:
        data["process_id"] = process_id

        if data["type"] == enums.TriggerType.CRON:
            data["date"] = None
            data["workqueue_id"] = None
            data["workqueue_scale_up_threshold"] = 0
            data["workqueue_resource_limit"] = 0

        if data["type"] == enums.TriggerType.DATE:
            data["cron"] = ""
            data["workqueue_id"] = None
            data["workqueue_scale_up_threshold"] = 0
            data["workqueue_resource_limit"] = 0

        if data["type"] == enums.TriggerType.WORKQUEUE:
            data["cron"] = ""
            data["date"] = None

        return repository.create(data)


@router.get("/{process_id}/trigger")
def get_triggers(
    process_id: int,
    include_deleted: bool = False,
    repository: ProcessRepository = Depends(get_repository(Process)),
    token: AccessToken = Depends(resolve_access_token),
) -> list[Trigger]:
    # Check if the process exists
    process = repository.get(process_id)

    if process is None:
        raise HTTPException(status_code=404, detail="Process not found")

    if process.deleted:
        raise HTTPException(status_code=403, detail="Process is deleted")

    if include_deleted:
        return list(process.triggers)

    return list(filter(lambda x: not x.deleted, process.triggers))
