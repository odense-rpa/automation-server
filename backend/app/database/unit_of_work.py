import abc

from contextlib import AbstractContextManager

from app.database import repository


class AbstractUnitOfWork(AbstractContextManager):
    processes: repository.AbstractProcessRepository
    triggers: repository.AbstractTriggerRepository
    credentials: repository.AbstractCredentialRepository
    resources: repository.AbstractResourceRepository
    sessions: repository.AbstractSessionRepository
    auditlogs: repository.AbstractAuditLogRepository
    work_items: repository.AbstractWorkItemRepository
    workqueues: repository.AbstractWorkqueueRepository

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
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

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
