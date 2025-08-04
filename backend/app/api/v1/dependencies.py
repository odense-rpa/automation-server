from typing import Optional
from datetime import datetime, timedelta
from fastapi import Depends, Query, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database.unit_of_work import AbstractUnitOfWork,UnitOfWork
from sqlmodel import Session
from typing import Annotated


from app.database.session import get_session

import app.database.repository as repositories
import app.database.models as models
import app.api.v1.schemas as schemas

from app.security import oauth2_scheme

from app.services import (
    AuditLogService,
    SessionService,
    ResourceService,
    WorkqueueService,
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

        if model == models.AuditLog:
            return repositories.AuditLogRepository(session)

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


def get_auditlog_service(
    repository: repositories.AuditLogRepository = Depends(
        get_repository(models.AuditLog)
    ),
) -> AuditLogService:
    return AuditLogService(repository)


def get_session_service(
    repository: repositories.SessionRepository = Depends(
        get_repository(models.Session)
    ),
    resource_repository: repositories.ResourceRepository = Depends(
        get_repository(models.Resource)
    ),
) -> SessionService:
    return SessionService(repository, resource_repository)


def get_resource_service(
    repository: repositories.ResourceRepository = Depends(
        get_repository(models.Resource)
    ),
    session_repository: repositories.SessionRepository = Depends(
        get_repository(models.Session)
    ),
) -> ResourceService:
    return ResourceService(repository, session_repository)


def get_paginated_search_params(
    page: int = Query(1, ge=1, description="Page number, starting from 1"),
    size: int = Query(50, ge=1, le=200, description="Number of items per page"),
    search: Optional[str] = Query(None, description="Search term"),
) -> schemas.PaginatedSearchParams:
    pagination = schemas.PaginationParams(page=page, size=size)
    return schemas.PaginatedSearchParams(pagination=pagination, search=search)


def resolve_access_token(
    token: str = Depends(oauth2_scheme),
    repository: repositories.AccessTokenRepository = Depends(
        get_repository(models.AccessToken)
    ),
) -> models.AccessToken:
    tokens = repository.get_all()

    # If there are no tokens in the system, we assume that we are in either install or development mode.
    if len(tokens) == 0:
        return models.AccessToken(
            id=0,
            token="development-token",
            identifier="development-token",
            expires_at=datetime.now() + timedelta(weeks=52),
            revoked=False,
        )

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if the token is in the tokens
    for t in tokens:
        if t.access_token == token and not t.deleted and t.expires_at > datetime.now():
            return t

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_unit_of_work(session: Session = Depends(get_session)) -> AbstractUnitOfWork:
    return UnitOfWork(session)

UnitOfWorkDep = Annotated[AbstractUnitOfWork, Depends(get_unit_of_work)]