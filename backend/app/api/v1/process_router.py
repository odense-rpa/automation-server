from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from app.database.models import Process, Trigger, AccessToken

from .schemas import ProcessCreate, ProcessUpdate, TriggerCreate
from .dependencies import resolve_access_token, get_unit_of_work
from app.database.unit_of_work import AbstractUnitOfWork

import app.enums as enums
from . import error_descriptions


router = APIRouter(prefix="/processes", tags=["Processes"])


# Dependency Injection local to this router


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


# Routes
@router.get("", responses=error_descriptions("Process", _403=True))
def get_processes(
    include_deleted: bool = False,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> list[Process]:
    with uow:
        return uow.processes.get_all(include_deleted)


@router.get(
    "/{process_id}",
    responses=error_descriptions("Process", _403=True, _404=True, _410=True),
)
def get_process(
    process: Process = Depends(get_process),
    token: AccessToken = Depends(resolve_access_token),
) -> Process:
    return process


@router.put(
    "/{process_id}",
    responses=error_descriptions("Process", _403=True, _404=True, _410=True),
)
def update_process(
    update: ProcessUpdate,
    process: Process = Depends(get_process),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> Process:
    with uow:
        return uow.processes.update(process, update.model_dump())


@router.post("", responses=error_descriptions("Process", _403=True))
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
    responses=error_descriptions("Process", _403=True, _404=True, _410=True)
    | {
        204: {
            "description": "Item deleted",
            "content": {
                "application/json": {"example": {"detail": "Process has been deleted"}}
            },
        }
    },
)
def delete_process(
    process: Process = Depends(get_process),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> None:
    with uow:
        uow.processes.delete(process)
        return


@router.post(
    "/{process_id}/trigger", responses=error_descriptions("Trigger", _403=True)
)
def create_trigger(
    trigger: TriggerCreate,
    process: Process = Depends(get_process),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> Trigger:
    data = trigger.model_dump()
    data["deleted"] = False

    with uow:
        data["process_id"] = process.id

        # TODO: This code belongs in the service layer, not the API layer
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

        return uow.triggers.create(data)


@router.get(
    "/{process_id}/trigger",
    responses=error_descriptions("Trigger", _403=True, _404=True, _410=True),
)
def get_triggers(
    include_deleted: bool = False,
    process: Process = Depends(get_process),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> list[Trigger]:
    with uow:
        if include_deleted:
            return list(process.triggers)

        return [x for x in process.triggers if not x.deleted]
