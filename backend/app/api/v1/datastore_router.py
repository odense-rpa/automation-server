from fastapi import APIRouter, Depends, HTTPException, Response

from app.database.models import AccessToken, Datastore
from app.database.unit_of_work import AbstractUnitOfWork
from app.services import DatastoreService
from app.services.datastore_service import (
    DatastoreConflict,
    DatastoreNameTaken,
    DatastoreNotFound,
    DatastoreTooLarge,
)

from . import error_descriptions
from .dependencies import (
    get_datastore_service,
    get_unit_of_work,
    resolve_access_token,
)
from .schemas import (
    DatastoreCreate,
    DatastoreRead,
    DatastoreSummary,
    DatastoreUpdate,
    DatastoreWrite,
)

router = APIRouter(prefix="/datastores", tags=["Datastores"])


async def get_datastore(
    datastore_id: int, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> Datastore:
    async with uow:
        datastore = await uow.datastores.get(datastore_id)

        if datastore is None:
            raise HTTPException(status_code=404, detail="Datastore not found")

        if datastore.deleted:
            raise HTTPException(status_code=410, detail="Datastore is gone")

        return datastore


def write_error(error: Exception) -> HTTPException:
    """Service exceptions as HTTP errors."""
    if isinstance(error, DatastoreConflict):
        return HTTPException(status_code=409, detail=str(error))
    if isinstance(error, DatastoreTooLarge):
        return HTTPException(status_code=413, detail=str(error))
    if isinstance(error, DatastoreNameTaken):
        return HTTPException(status_code=422, detail="Datastore name already exists")
    if isinstance(error, DatastoreNotFound):
        return HTTPException(status_code=404, detail="Datastore not found")
    raise error


WRITE_ERRORS = (
    DatastoreConflict,
    DatastoreTooLarge,
    DatastoreNameTaken,
    DatastoreNotFound,
)

RESPONSE_STATES = error_descriptions("Datastore", _404=True, _410=True, _403=True)
CONFLICT = {409: {"description": "Changed by someone else since expected_version"}}
TOO_LARGE = {413: {"description": "Document larger than the datastore size limit"}}
CREATED = {201: {"description": "Datastore created"}}


@router.get("", responses=error_descriptions("Datastore", _403=True))
async def get_datastores(
    include_deleted: bool = False,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> list[DatastoreSummary]:
    # No documents in the listing: they can be large and aren't needed here
    async with uow:
        result = await uow.datastores.get_all(include_deleted)
        result.sort(key=lambda x: x.name)
        return [DatastoreSummary(**d.model_dump(exclude={"data"})) for d in result]


@router.post("", responses=error_descriptions("Datastore", _403=True) | TOO_LARGE)
async def create_datastore(
    datastore: DatastoreCreate,
    service: DatastoreService = Depends(get_datastore_service),
    token: AccessToken = Depends(resolve_access_token),
) -> DatastoreRead:
    try:
        return await service.create(
            datastore.name, datastore.description, datastore.data
        )
    except WRITE_ERRORS as error:
        raise write_error(error)


# Declared before /{datastore_id}, which would otherwise try to parse
# "by_name" as an id


@router.get(
    "/by_name/{datastore_name}",
    responses=error_descriptions("Datastore", _404=True, _403=True),
)
async def get_datastore_by_name(
    datastore_name: str,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> DatastoreRead:
    async with uow:
        datastore = await uow.datastores.get_by_name(datastore_name)

        if datastore is None:
            raise HTTPException(status_code=404, detail="Datastore not found")

        return datastore


@router.put(
    "/by_name/{datastore_name}",
    responses=CREATED
    | error_descriptions("Datastore", _404=True, _403=True)
    | CONFLICT
    | TOO_LARGE,
)
async def write_datastore_by_name(
    datastore_name: str,
    write: DatastoreWrite,
    response: Response,
    service: DatastoreService = Depends(get_datastore_service),
    token: AccessToken = Depends(resolve_access_token),
) -> DatastoreRead:
    """Write a datastore's document, creating the datastore if it doesn't exist."""
    try:
        datastore, created = await service.write_by_name(
            datastore_name, write.data, write.expected_version
        )
    except WRITE_ERRORS as error:
        raise write_error(error)

    if created:
        response.status_code = 201
    return datastore


@router.get("/{datastore_id}", responses=RESPONSE_STATES)
async def read_datastore(
    datastore: Datastore = Depends(get_datastore),
    token: AccessToken = Depends(resolve_access_token),
) -> DatastoreRead:
    return datastore


@router.put("/{datastore_id}", responses=RESPONSE_STATES | CONFLICT | TOO_LARGE)
async def update_datastore(
    update: DatastoreUpdate,
    datastore: Datastore = Depends(get_datastore),
    service: DatastoreService = Depends(get_datastore_service),
    token: AccessToken = Depends(resolve_access_token),
) -> DatastoreRead:
    try:
        return await service.write(
            datastore,
            update.expected_version,
            data=update.data,
            name=update.name,
            description=update.description,
        )
    except WRITE_ERRORS as error:
        raise write_error(error)


@router.delete("/{datastore_id}", status_code=204, responses=RESPONSE_STATES)
async def delete_datastore(
    datastore: Datastore = Depends(get_datastore),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> None:
    async with uow:
        await uow.datastores.delete(datastore)
