from fastapi import APIRouter, Depends, Response
from fastapi.exceptions import HTTPException

from app.database.repository import ProcessRepository, TriggerRepository
from app.database.models import Process, Trigger

from .schemas import ProcessCreate, ProcessUpdate, TriggerCreate
from .dependencies import get_repository

import app.enums as enums

router = APIRouter(prefix="/processes", tags=["Processes"])


@router.get("")
def get_processes(
    include_deleted: bool = False,
    repository: ProcessRepository = Depends(get_repository(Process)),
) -> list[Process]:
    return repository.get_all(include_deleted)


@router.get("/{process_id}")
def get_process(
    process_id: str,
    repository: ProcessRepository = Depends(get_repository(Process)),
) -> Process:
    process = repository.get(process_id)

    if process is None:
        raise HTTPException(status_code=404, detail="Process not found")

    if process.deleted:
        raise HTTPException(status_code=403, detail="Process is deleted")

    return process


@router.put("/{process_id}")
def update_process(
    process_id: str,
    update: ProcessUpdate,
    repository: ProcessRepository = Depends(get_repository(Process)),
) -> Process:
    process = repository.get(process_id)

    if process is None:
        raise HTTPException(status_code=404, detail="Process not found")

    if process.deleted:
        raise HTTPException(status_code=403, detail="Process is deleted")

    return repository.update(process, update.model_dump())


@router.post("")
def create_process(
    process: ProcessCreate,
    repository: ProcessRepository = Depends(get_repository(Process)),
) -> Process:
    data = process.model_dump()
    data["deleted"] = False

    return repository.create(data)


@router.delete("/{process_id}")
def delete_process(
    process_id: str,
    repository: ProcessRepository = Depends(get_repository(Process)),
) -> Response:
    process = repository.get(process_id)

    if process is None:
        raise HTTPException(status_code=404, detail="Process not found")

    return repository.delete(process)

@router.post("/{process_id}/trigger")
def create_trigger(
    process_id: int,
    trigger: TriggerCreate,
    repository: TriggerRepository = Depends(get_repository(Trigger)),
    process_repository: ProcessRepository = Depends(get_repository(Process)),
) -> Trigger:
    
    data = trigger.model_dump()
    data["deleted"] = False
    
    # Check if the process exists
    process = process_repository.get(process_id)

    if process is None:
        raise HTTPException(status_code=404, detail="Process not found")
    
    data["process_id"] = process_id

    if(data["type"] == enums.TriggerType.CRON):
        data["date"] = None
        data["workqueue_id"] = None
        data["workqueue_scale_up_threshold"] = 0
        data["workqueue_resource_limit"] = 0

    if(data["type"] == enums.TriggerType.DATE):
        data["cron"] = ""
        data["workqueue_id"] = None
        data["workqueue_scale_up_threshold"] = 0
        data["workqueue_resource_limit"] = 0

    if(data["type"] == enums.TriggerType.WORKQUEUE):
        data["cron"] = ""
        data["date"] = None


    return repository.create(data)

@router.get("/{process_id}/trigger")
def get_triggers(
    process_id: int,
    include_deleted: bool = False,
    repository: ProcessRepository = Depends(get_repository(Process)),
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
