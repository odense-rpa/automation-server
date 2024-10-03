from fastapi import Depends, APIRouter, HTTPException

from app.database.repository import CredentialRepository
from app.database.models import Credential, AccessToken

from .schemas import CredentialCreate, CredentialUpdate
from .dependencies import get_repository, resolve_access_token

router = APIRouter(prefix="/credentials", tags=["Credentials"])


@router.get("")
def get_credentials(
    include_deleted: bool = False,
    repository: CredentialRepository = Depends(get_repository(Credential)),
    token: AccessToken = Depends(resolve_access_token),
) -> list[Credential]:
    list = repository.get_all(include_deleted)

    list.sort(key=lambda x: x.name)
    return list


@router.get("/{credential_id}")
def get_credential(
    credential_id: str,
    repository: CredentialRepository = Depends(get_repository(Credential)),
    token: AccessToken = Depends(resolve_access_token),
) -> Credential:
    credential = repository.get(credential_id)

    if credential is None:
        raise HTTPException(status_code=404, detail="Credential not found")

    if credential.deleted:
        raise HTTPException(status_code=403, detail="Credential is deleted")

    return credential


@router.put("/{credential_id}")
def update_credential(
    credential_id: str,
    update: CredentialUpdate,
    repository: CredentialRepository = Depends(get_repository(Credential)),
    token: AccessToken = Depends(resolve_access_token),
) -> Credential:
    credential = repository.get(credential_id)

    if credential is None:
        raise HTTPException(status_code=404, detail="Credential not found")

    if credential.deleted:
        raise HTTPException(status_code=403, detail="Credential is deleted")

    return repository.update(credential, update.model_dump())


@router.post("")
def create_credential(
    credential: CredentialCreate,
    repository: CredentialRepository = Depends(get_repository(Credential)),
    token: AccessToken = Depends(resolve_access_token),
) -> Credential:
    data = credential.model_dump()
    data["deleted"] = False

    return repository.create(data)


@router.delete("/{credential_id}")
def delete_credential(
    credential_id: str,
    repository: CredentialRepository = Depends(get_repository(Credential)),
    token: AccessToken = Depends(resolve_access_token),
) -> Credential:
    credential = repository.get(credential_id)

    if credential is None:
        raise HTTPException(status_code=404, detail="Credential not found")

    if credential.deleted:
        raise HTTPException(status_code=403, detail="Credential is deleted")

    return repository.delete(credential)
