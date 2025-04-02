from fastapi import APIRouter, Depends, HTTPException

from app.database.models import Resource, AccessToken


from app.services import ResourceService
from app.database.unit_of_work import AbstractUnitOfWork

from .schemas import ResourceCreate, ResourceUpdate
from .dependencies import get_resource_service, resolve_access_token, get_unit_of_work

from . import get_standard_error_descriptions

router = APIRouter(prefix="/resources", tags=["Resources"])

# Dependency Injection local to this router


def get_resource(
    resource_id: int, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> Resource:
    with uow:
        resource = uow.resources.get(resource_id)

        if resource is None:
            raise HTTPException(status_code=404, detail="Resource not found")

        if resource.deleted:
            raise HTTPException(status_code=410, detail="Resource is gone")

        return resource


def get_resource_include_deleted(
    resource_id: int, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> Resource:
    with uow:
        resource = uow.resources.get(resource_id)

        if resource is None:
            raise HTTPException(status_code=404, detail="Resource not found")

        return resource


# Error responses

RESPONSE_STATES = get_standard_error_descriptions("Resource")


@router.get("")
def get_resources(
    include_deleted: bool = False,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    service: ResourceService = Depends(get_resource_service),
    token: AccessToken = Depends(resolve_access_token),
) -> list[Resource]:
    service.update_availability()

    # Return all resources that are not deleted and have been seen in the last 10 minutes
    with uow:
        return uow.resources.get_all(include_deleted=include_deleted)


@router.get("/{resource_id}", responses=RESPONSE_STATES)
def get_resource(
    resource: Resource = Depends(get_resource),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> Resource:
    return resource


@router.put("/{resource_id}", responses=RESPONSE_STATES)
def update_resource(
    update: ResourceUpdate,
    resource: Resource = Depends(get_resource_include_deleted),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    service: ResourceService = Depends(get_resource_service),
    token: AccessToken = Depends(resolve_access_token),
) -> Resource:
    if update.fqdn != resource.fqdn:
        raise HTTPException(status_code=400, detail="FQDN cannot be changed")

    return service.enroll(update.fqdn, update.name, update.capabilities)


@router.put("/{resource_id}/ping", response_model=bool, responses=RESPONSE_STATES)
def ping_resource(
    resource: Resource = Depends(get_resource_include_deleted),
    service: ResourceService = Depends(get_resource_service),
    token: AccessToken = Depends(resolve_access_token),
) -> bool:
    service.keep_alive(resource)

    return True


@router.post("")
def create_resource(
    resource: ResourceCreate,
    service: ResourceService = Depends(get_resource_service),
    token: AccessToken = Depends(resolve_access_token),
) -> Resource:
    return service.enroll(resource.fqdn, resource.name, resource.capabilities)
