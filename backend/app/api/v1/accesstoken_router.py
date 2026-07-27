from fastapi import APIRouter, Depends, HTTPException, Response

from app.database.models import AccessToken
from app.database.repository import AccessTokenRepository

from .dependencies import get_repository, resolve_access_token
from .schemas import AccessTokenCreate, AccessTokenRead

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

    active_tokens = await repository.get_all()
    if len(active_tokens) <= 1:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete the last access token. Create a replacement "
            "token first — with no tokens the API would run without "
            "authentication.",
        )

    await repository.delete(access_token)

    # Return 204
    return Response(status_code=204)
