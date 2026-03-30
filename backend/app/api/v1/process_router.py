from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

import app.enums as enums
from app.database.models import AccessToken, Process, Trigger
from app.database.unit_of_work import AbstractUnitOfWork

from . import error_descriptions
from .dependencies import get_unit_of_work, resolve_access_token
from .schemas import ProcessCreate, ProcessUpdate, TriggerCreate

router = APIRouter(prefix="/processes", tags=["Processes"])


# Dependency Injection local to this router


async def get_process(
    process_id: int, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> Process:
    async with uow:
        process = await uow.processes.get(process_id)

        if process is None:
            raise HTTPException(status_code=404, detail="Process not found")

        if process.deleted:
            raise HTTPException(status_code=410, detail="Process is gone")

        return process


# Routes
@router.get("", responses=error_descriptions("Process", _403=True))
async def get_processes(
    include_deleted: bool = False,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> list[Process]:
    async with uow:
        return await uow.processes.get_all(include_deleted)


@router.get(
    "/{process_id}",
    responses=error_descriptions("Process", _403=True, _404=True, _410=True),
)
async def get_process(
    process: Process = Depends(get_process),
    token: AccessToken = Depends(resolve_access_token),
) -> Process:
    return process


@router.put(
    "/{process_id}",
    responses=error_descriptions("Process", _403=True, _404=True, _410=True),
)
async def update_process(
    update: ProcessUpdate,
    process: Process = Depends(get_process),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> Process:
    async with uow:
        return await uow.processes.update(process, update.model_dump())


@router.post("", responses=error_descriptions("Process", _403=True))
async def create_process(
    process: ProcessCreate,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> Process:
    async with uow:
        data = process.model_dump(exclude_unset=True)
        data["deleted"] = False

        return await uow.processes.create(data)


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
async def delete_process(
    process: Process = Depends(get_process),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> None:
    async with uow:
        await uow.processes.delete(process)
        return


@router.post(
    "/{process_id}/trigger", responses=error_descriptions("Trigger", _403=True)
)
async def create_trigger(
    trigger: TriggerCreate,
    process: Process = Depends(get_process),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> Trigger:
    data = trigger.model_dump()
    data["deleted"] = False

    async with uow:
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

        return await uow.triggers.create(data)


@router.get(
    "/{process_id}/trigger",
    responses=error_descriptions("Trigger", _403=True, _404=True, _410=True),
)
async def get_triggers(
    include_deleted: bool = False,
    process: Process = Depends(get_process),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> list[Trigger]:
    async with uow:
        triggers = await uow.triggers.filter(Trigger.process_id == process.id)
        if include_deleted:
            return list(triggers)
        return [x for x in triggers if not x.deleted]
