import abc

from contextlib import AbstractAsyncContextManager

from app.database import repository


class AbstractUnitOfWork(AbstractAsyncContextManager):
    processes: repository.AbstractProcessRepository
    triggers: repository.AbstractTriggerRepository
    credentials: repository.AbstractCredentialRepository
    resources: repository.AbstractResourceRepository
    sessions: repository.AbstractSessionRepository
    auditlogs: repository.AbstractAuditLogRepository
    work_items: repository.AbstractWorkItemRepository
    workqueues: repository.AbstractWorkqueueRepository
    incidents: repository.AbstractIncidentRepository

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            await self.rollback()

    @abc.abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self):
        raise NotImplementedError


class UnitOfWork(AbstractUnitOfWork):
    def __init__(self, session) -> None:
        self.session = session
        self.processes = repository.ProcessRepository(session)
        self.triggers = repository.TriggerRepository(session)
        self.credentials = repository.CredentialRepository(session)
        self.resources = repository.ResourceRepository(session)
        self.sessions = repository.SessionRepository(session)
        self.auditlogs = repository.AuditLogRepository(session)
        self.work_items = repository.WorkItemRepository(session)
        self.workqueues = repository.WorkqueueRepository(session)
        self.incidents = repository.IncidentRepository(session)

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
