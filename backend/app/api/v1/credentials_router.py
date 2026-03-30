from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from app.database.models import Credential, AccessToken
from app.database.unit_of_work import AbstractUnitOfWork
from .schemas import CredentialCreate, CredentialUpdate
from .dependencies import get_unit_of_work, resolve_access_token
from . import error_descriptions

# Dependency Injection local to this router


async def get_credential(
    credential_id: int, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> Credential:
    async with uow:
        credential = await uow.credentials.get(credential_id)

        if credential is None:
            raise HTTPException(status_code=404, detail="Credential not found")

        if credential.deleted:
            raise HTTPException(status_code=410, detail="Credential is gone")

        return credential


# Error responses

RESPONSE_STATES = error_descriptions("Credential", _404=True, _410=True, _403=True)

# Router

router = APIRouter(prefix="/credentials", tags=["Credentials"])


@router.get("", responses=error_descriptions("Credential", _403=True))
async def get_credentials(
    include_deleted: bool = False,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> list[Credential]:
    async with uow:
        result = await uow.credentials.get_all(include_deleted)

        result.sort(key=lambda x: x.name)
        return result


@router.get("/{credential_id}", responses=RESPONSE_STATES)
async def get_credential(
    credential: Credential = Depends(get_credential),
    token: AccessToken = Depends(resolve_access_token),
) -> Credential:
    return credential


@router.get("/by_name/{credential_name}", responses=RESPONSE_STATES)
async def get_credential_by_name(
    credential_name: str,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> Credential:
    async with uow:
        credential = await uow.credentials.get_by_name(credential_name)

        if credential is None:
            raise HTTPException(status_code=404, detail="Credential not found")

        if credential.deleted:
            raise HTTPException(status_code=410, detail="Credential is gone")

        return credential


@router.put("/{credential_id}", responses=RESPONSE_STATES)
async def update_credential(
    update: CredentialUpdate,
    credential: Credential = Depends(get_credential),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> Credential:
    async with uow:
        return await uow.credentials.update(credential, update.model_dump())


@router.post("", responses=error_descriptions("Credential", _403=True))
async def create_credential(
    credential: CredentialCreate,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> Credential:
    try:
        async with uow:
            data = credential.model_dump()
            data["deleted"] = False

            return await uow.credentials.create(data)
    except ValueError:
        raise HTTPException(status_code=422, detail="JSON data is invalid")
    except IntegrityError:
        raise HTTPException(status_code=422, detail="Credential name already exists")


@router.delete(
    "/{credential_id}",
    status_code=204,
    responses={
        204: {
            "description": "Item deleted",
            "content": {
                "application/json": {"example": {"detail": "Process has been deleted"}}
            },
        }
    }
    | RESPONSE_STATES,
)
async def delete_credential(
    credential: Credential = Depends(get_credential),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> None:
    async with uow:
        await uow.credentials.delete(credential)

    return
