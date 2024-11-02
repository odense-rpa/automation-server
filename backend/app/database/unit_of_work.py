import abc

from contextlib import AbstractContextManager

from app.database import repository


class AbstractUnitOfWork(AbstractContextManager):
    processes: repository.AbstractProcessRepository
    triggers: repository.AbstractTriggerRepository
    credentials: repository.AbstractCredentialRepository

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

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
