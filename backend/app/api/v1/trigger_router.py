from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from typing import List, Dict, Any
from datetime import datetime

from app.database.models import Trigger, AccessToken

from app.database.unit_of_work import AbstractUnitOfWork

from .schemas import TriggerUpdate
from .dependencies import get_unit_of_work, resolve_access_token

from . import error_descriptions
from app.scheduler.upcoming_calculator import get_upcoming_executions

router = APIRouter(prefix="/triggers", tags=["Triggers"])

# Dependency Injection local to this router


def get_trigger(
    trigger_id: int, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> Trigger:
    with uow:
        trigger = uow.triggers.get(trigger_id)

        if trigger is None:
            raise HTTPException(status_code=404, detail="Trigger not found")

        if trigger.deleted:
            raise HTTPException(status_code=410, detail="Trigger is gone")

        return trigger




# Get triggers
@router.get(
    "", response_model=list[Trigger], responses=error_descriptions("Trigger", _403=True)
)
async def get_triggers(
    include_deleted: bool = False,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
):
    return uow.triggers.get_all(include_deleted=include_deleted)


# Update a trigger
@router.put(
    "/{trigger_id}",
    responses=error_descriptions("Trigger", _403=True, _404=True, _410=True),
)
async def update_trigger(
    update: TriggerUpdate,
    trigger: Trigger = Depends(get_trigger),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> Trigger:
    with uow:
        return uow.triggers.update(trigger, update.model_dump())


# Delete a trigger
@router.delete(
    "/{trigger_id}",
    responses=error_descriptions("Trigger", _204=True, _403=True, _404=True, _410=True),
    status_code=204,
)
async def delete_trigger(
    trigger: Trigger = Depends(get_trigger),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
):
    with uow:
        uow.triggers.delete(trigger)

    return


# Get upcoming executions
@router.get(
    "/upcoming",
    response_model=List[Dict[str, Any]],
    responses=error_descriptions("Trigger", _403=True),
)
async def get_upcoming_trigger_executions(
    hours_ahead: int = Query(24, description="Hours ahead to look for executions", ge=1, le=168),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
):
    """Get upcoming trigger executions within the specified time window."""
    with uow:
        # Get all active triggers
        triggers = uow.triggers.get_all(include_deleted=False)
        active_triggers = [t for t in triggers if t.enabled]
        
        # Get upcoming executions
        upcoming = get_upcoming_executions(active_triggers, hours_ahead)
        
        # Enhance with process information
        result = []
        for execution in upcoming:
            trigger = execution['trigger']
            process = uow.processes.get(trigger.process_id)
            
            if process and not process.deleted:
                result.append({
                    'trigger_id': trigger.id,
                    'process_id': trigger.process_id,
                    'process_name': process.name,
                    'process_description': process.description,
                    'next_execution': execution['next_execution'].isoformat(),
                    'trigger_type': execution['trigger_type'],
                    'parameters': execution['parameters'],
                    'cron': trigger.cron if trigger.type.value == 'cron' else None,
                    'date': trigger.date.isoformat() if trigger.date else None
                })
        
        return result
