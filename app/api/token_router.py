from typing import Annotated
from datetime import datetime

from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from app.database.repository import AccessTokenRepository
from app.database.models import AccessToken

# from .schemas import CredentialCreate, CredentialUpdate
from app.api.v1.dependencies import get_repository


router = APIRouter(prefix="/token", tags=["Oauth2"])


@router.post("/")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    repository: AccessTokenRepository = Depends(get_repository(AccessToken)),
):
    tokens = repository.get_all()
    
    if form_data.password in [token.access_token for token in tokens if not token.deleted and token.expires_at > datetime.now()]:
        return {"access_token": form_data.password, "token_type": "bearer"}

    raise HTTPException(status_code=400, detail="Incorrect username or password")