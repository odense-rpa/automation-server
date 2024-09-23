from datetime import datetime, timedelta
import secrets
from fastapi import APIRouter, Depends, Response, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.database.repository import AccessTokenRepository
from typing import List, Annotated, Optional
from app.database.models import AccessToken
from .v1.schemas import AccessTokenRead

from app.services import ClientCredentialService
from app.api.v1.dependencies import get_client_credential_service, get_repository

from app.security import OAuth2ClientCredentials, resolve_client_credentials, resolve_form_credentials

# from .v1.dependencies import get_repository

router = APIRouter(prefix="/token", tags=["Tokens"])


@router.post("/")
def authorize(
    form_data: Optional[OAuth2PasswordRequestForm]  = Depends(resolve_form_credentials),
    client_credentials: OAuth2ClientCredentials = Depends(resolve_client_credentials),
    client_credential_service: ClientCredentialService = Depends(get_client_credential_service),
    access_token_repository: AccessTokenRepository = Depends(get_repository(AccessToken))
):

    if client_credentials:
        if client_credential_service.validate_client(client_credentials.client_id, client_credentials.client_secret):
            
            token = access_token_repository.generate_access_token()
            
            return {"access_token": token.token, "token_type": "bearer"}
        else:
            raise HTTPException(status_code=400, detail="Invalid credentials")
    
    if form_data:
        return {"access_token": form_data.username, "token_type": "bearer"}
    
    
    raise HTTPException(status_code=400, detail="Invalid credentials")

