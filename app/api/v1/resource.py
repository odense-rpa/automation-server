from fastapi import APIRouter, Depends, HTTPException

from app.database.models import Resource, AccessToken
from app.database.repository import ResourceRepository
from app.services import ResourceService

from .schemas import ResourceCreate, ResourceUpdate
from .dependencies import get_repository, get_resource_service, resolve_access_token


router = APIRouter(prefix="/resources", tags=["Resources"])


@router.get("")
def get_resources(
    include_expired: bool = False,
    repository: ResourceRepository = Depends(get_repository(Resource)),
    service: ResourceService = Depends(get_resource_service),
    token: AccessToken = Depends(resolve_access_token),
) -> list[Resource]:
    service.update_availability()

    # Return all resources that are not deleted and have been seen in the last 10 minutes
    resources = repository.get_all(include_deleted=False)

    if include_expired:
        return resources

    return [x for x in resources if x.available]


@router.get("/{resource_id}")
def get_resource(
    resource_id: str,
    repository: ResourceRepository = Depends(get_repository(Resource)),
    token: AccessToken = Depends(resolve_access_token),
) -> Resource:
    resource = repository.get(resource_id)

    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")

    return resource


@router.put("/{resource_id}")
def update_resource(
    resource_id: str,
    update: ResourceUpdate,
    repository: ResourceRepository = Depends(get_repository(Resource)),
    service: ResourceService = Depends(get_resource_service),
    token: AccessToken = Depends(resolve_access_token),
) -> Resource:
    resource = repository.get(resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")

    if update.fqdn != resource.fqdn:
        raise HTTPException(status_code=400, detail="FQDN cannot be changed")

    return service.enroll(update.fqdn, update.name, update.capabilities)


@router.put("/{resource_id}/ping")
def ping_resource(
    resource_id: str,
    repository: ResourceRepository = Depends(get_repository(Resource)),
    service: ResourceService = Depends(get_resource_service),
    token: AccessToken = Depends(resolve_access_token),
) -> bool:
    resource = repository.get(resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")

    service.keep_alive(resource)

    return True


@router.post("")
def create_resource(
    resource: ResourceCreate,
    service: ResourceService = Depends(get_resource_service),
    token: AccessToken = Depends(resolve_access_token),
) -> Resource:
    return service.enroll(resource.fqdn, resource.name, resource.capabilities)
