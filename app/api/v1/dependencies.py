from typing import Optional
import datetime
from fastapi import Depends, Query, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database.session import get_session

import app.database.repository as repositories
import app.database.models as models
import app.api.v1.schemas as schemas

from app.services import (
    SessionLogService,
    SessionService,
    ResourceService,
    WorkqueueService,
    ClientCredentialService
)


def get_repository(model):
    def get(session=Depends(get_session)):
        if model == models.Workqueue:
            return repositories.WorkqueueRepository(session)

        # Generate for all model repositories
        if model == models.WorkItem:
            return repositories.WorkItemRepository(session)

        if model == models.Process:
            return repositories.ProcessRepository(session)

        if model == models.Credential:
            return repositories.CredentialRepository(session)

        if model == models.Resource:
            return repositories.ResourceRepository(session)

        if model == models.Session:
            return repositories.SessionRepository(session)

        if model == models.Trigger:
            return repositories.TriggerRepository(session)

        if model == models.SessionLog:
            return repositories.SessionLogRepository(session)

        if model == models.AccessToken:
            return repositories.AccessTokenRepository(session)
        
        if model == models.ClientCredential:
            return repositories.ClientCredentialRepository(session)
        
        # Add more repositories here

    return get


def get_workqueue_service(
    repository: repositories.WorkqueueRepository = Depends(
        get_repository(models.Workqueue)
    ),
) -> WorkqueueService:
    return WorkqueueService(repository)


def get_sessionlog_service(
    repository: repositories.SessionLogRepository = Depends(
        get_repository(models.SessionLog)
    ),
) -> SessionLogService:
    return SessionLogService(repository)


def get_session_service(
    repository: repositories.SessionRepository = Depends(
        get_repository(models.Session)
    ),
) -> SessionService:
    return SessionService(repository)


def get_resource_service(
    repository: repositories.ResourceRepository = Depends(
        get_repository(models.Resource)
    ),
    session_repository: repositories.SessionRepository = Depends(
        get_repository(models.Session)
    ),
) -> ResourceService:
    return ResourceService(repository, session_repository)

def get_client_credential_service(
    repository: repositories.ClientCredentialRepository = Depends(
        get_repository(models.ClientCredential)
    )):
    return ClientCredentialService(repository)


def get_paginated_search_params(
    page: int = Query(1, ge=1, description="Page number, starting from 1"),
    size: int = Query(50, ge=1, le=200, description="Number of items per page"),
    search: Optional[str] = Query(None, description="Search term"),
) -> schemas.PaginatedSearchParams:
    pagination = schemas.PaginationParams(page=page, size=size)
    return schemas.PaginatedSearchParams(pagination=pagination, search=search)


bearer_scheme = HTTPBearer()

def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    repository = Depends(get_repository(models.AccessToken)),
):
    token = credentials.credentials

    pat = repository.get_by_token(token)

    if not pat or (pat.expires_at and pat.expires_at < datetime.now()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return pat.id  # or return the user object if you prefer