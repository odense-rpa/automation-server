from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from app.database import crypto
from app.database.models import AccessToken, Credential
from app.database.unit_of_work import AbstractUnitOfWork

from . import error_descriptions
from .dependencies import get_unit_of_work, resolve_access_token
from .schemas import (
    CredentialCreate,
    CredentialEncryptionStatus,
    CredentialRead,
    CredentialReencryptResult,
    CredentialUpdate,
)


def to_credential_read(
    credential: Credential, unencrypted_ids: set[int]
) -> CredentialRead:
    return CredentialRead(
        **credential.model_dump(), encrypted=credential.id not in unencrypted_ids
    )

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
) -> list[CredentialRead]:
    async with uow:
        result = await uow.credentials.get_all(include_deleted)
        unencrypted_ids = await uow.credentials.get_unencrypted_ids()

        result.sort(key=lambda x: x.name)
        return [to_credential_read(c, unencrypted_ids) for c in result]


# Declared before /{credential_id}: that route parses the path segment as an
# int, so a later declaration would be shadowed and answer 422.
@router.get("/encryption", responses=error_descriptions("Credential", _403=True))
async def get_encryption_status(
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> CredentialEncryptionStatus:
    """Report whether credentials are encrypted at rest."""
    async with uow:
        unencrypted_ids = await uow.credentials.get_unencrypted_ids()
        return CredentialEncryptionStatus(
            key_configured=crypto.is_configured(),
            unencrypted_count=len(unencrypted_ids),
        )


@router.post(
    "/reencrypt",
    responses={
        409: {
            "description": "No encryption key is configured",
            "content": {
                "application/json": {
                    "example": {"detail": "No encryption key is configured"}
                }
            },
        }
    }
    | error_descriptions("Credential", _403=True),
)
async def reencrypt_credentials(
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> CredentialReencryptResult:
    """Rewrite every plaintext credential so it is stored encrypted.

    Credentials created before an encryption key was configured stay
    plaintext until they are written again. This does that in one pass.
    """
    if not crypto.is_configured():
        raise HTTPException(
            status_code=409,
            detail=(
                "No encryption key is configured. Set ENCRYPTION_KEY on the "
                "server and restart it before re-encrypting credentials."
            ),
        )

    async with uow:
        reencrypted = await uow.credentials.reencrypt_unencrypted()
        remaining = len(await uow.credentials.get_unencrypted_ids())

        return CredentialReencryptResult(
            reencrypted=reencrypted, remaining=remaining
        )


@router.get("/{credential_id}", responses=RESPONSE_STATES)
async def read_credential(
    credential: Credential = Depends(get_credential),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> CredentialRead:
    async with uow:
        unencrypted_ids = await uow.credentials.get_unencrypted_ids()
        return to_credential_read(credential, unencrypted_ids)


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
) -> CredentialRead:
    async with uow:
        updated = await uow.credentials.update(credential, update.model_dump())
        unencrypted_ids = await uow.credentials.get_unencrypted_ids()
        return to_credential_read(updated, unencrypted_ids)


@router.post("", responses=error_descriptions("Credential", _403=True))
async def create_credential(
    credential: CredentialCreate,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
    token: AccessToken = Depends(resolve_access_token),
) -> CredentialRead:
    try:
        async with uow:
            data = credential.model_dump()
            data["deleted"] = False

            created = await uow.credentials.create(data)
            unencrypted_ids = await uow.credentials.get_unencrypted_ids()
            return to_credential_read(created, unencrypted_ids)
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
