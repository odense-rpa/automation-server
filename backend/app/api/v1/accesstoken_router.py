from fastapi import Depends, HTTPException, APIRouter, Response

from app.database.repository import AccessTokenRepository
from app.database.models import AccessToken

from .dependencies import get_repository, resolve_access_token
from .schemas import AccessTokenRead, AccessTokenCreate

router = APIRouter(prefix="/accesstokens", tags=["Access Tokens"])


@router.get("")
async def get_access_tokens(
    include_deleted: bool = False,
    repository: AccessTokenRepository = Depends(get_repository(AccessToken)),
    token: AccessToken = Depends(resolve_access_token),
) -> list[AccessTokenRead]:
    list = await repository.get_all(include_deleted)

    list.sort(key=lambda x: x.identifier)
    return list


@router.get("/{access_token_id}")
async def get_access_token(
    access_token_id: str,
    repository: AccessTokenRepository = Depends(get_repository(AccessToken)),
    token: AccessToken = Depends(resolve_access_token),
) -> AccessTokenRead:
    access_token = await repository.get(access_token_id)

    if access_token is None:
        raise HTTPException(status_code=404, detail="Access Token not found")

    if access_token.deleted:
        raise HTTPException(status_code=403, detail="Access Token is deleted")

    return access_token


@router.post("")
async def create_access_token(
    identifier: AccessTokenCreate,
    repository: AccessTokenRepository = Depends(get_repository(AccessToken)),
    token: AccessToken = Depends(resolve_access_token),
) -> AccessToken:
    return await repository.create(identifier.identifier)


@router.delete("/{access_token_id}")
async def delete_access_token(
    access_token_id: str,
    repository: AccessTokenRepository = Depends(get_repository(AccessToken)),
    token: AccessToken = Depends(resolve_access_token),
) -> Response:
    access_token = await repository.get(access_token_id)

    if access_token is None:
        raise HTTPException(status_code=404, detail="Access Token not found")

    if access_token.deleted:
        raise HTTPException(status_code=403, detail="Access Token is deleted")

    await repository.delete(access_token)

    # Return 204
    return Response(status_code=204)
