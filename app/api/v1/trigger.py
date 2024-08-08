from fastapi import APIRouter, Depends, Response
from fastapi.exceptions import HTTPException

from app.database.repository import TriggerRepository
from app.database.models import Trigger

from .schemas import TriggerCreate, TriggerUpdate
from .dependencies import get_repository

import app.enums as enums

router = APIRouter(prefix="/triggers", tags=["Triggers"])


# Get triggers
@router.get("", response_model=list[Trigger])
async def get_triggers(
    include_deleted: bool = False,
    repository: TriggerRepository = Depends(get_repository(Trigger)),
):
    return repository.get_all(include_deleted=include_deleted)

# Update a trigger
@router.put("/{trigger_id}", response_model=Trigger)
async def update_trigger(
    trigger_id: int,
    trigger: TriggerUpdate,
    repository: TriggerRepository = Depends(get_repository(Trigger)),
):
    db_trigger = repository.get(trigger_id)
    if not db_trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")

    updated_trigger = repository.update(db_trigger, trigger.model_dump())

    return updated_trigger

# Delete a trigger
@router.delete("/{trigger_id}")
async def delete_trigger(
    trigger_id: int,
    repository: TriggerRepository = Depends(get_repository(Trigger)),
):
    # Does trigger exist?¨
    db_trigger = repository.get(trigger_id)
    if not db_trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")

    repository.delete(db_trigger)
    return Response(status_code=204)
