from typing import Generic, TypeVar, List, Optional
from datetime import datetime, timedelta

from sqlalchemy import BinaryExpression, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from sqlmodel import Session, select

from app.database import models
import app.enums as enums

import secrets

Model = TypeVar("Model", bound=models.Base)


class DatabaseRepository(Generic[Model]):
    """Repository for performing database queries."""

    def __init__(self, model: type[Model], session: Session) -> None:
        self.model = model
        self.session = session

    def create(self, data: dict) -> Model:
        instance = self.model(**data)
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def get(self, pk: int) -> Model | None:
        return self.session.get(self.model, pk)

    def update(self, instance: Model, data: dict) -> Model:
        for field, value in data.items():
            setattr(instance, field, value)

        if hasattr(instance, "updated_at"):
            instance.updated_at = datetime.now()

        self.session.commit()
        self.session.refresh(instance)
        return instance

    def delete(self, instance: Model) -> Model:
        # If self.model has a deleted field, set it to True
        if hasattr(instance, "deleted"):
            setattr(instance, "deleted", True)
            return self.update(
                instance, {"deleted": True, "updated_at": datetime.now()}
            )

        # Otherwise, delete the instance
        self.session.delete(instance)
        self.session.commit()
        return instance

    def get_all(self, include_deleted=False) -> list[Model]:
        query = select(self.model)

        if hasattr(self.model, "deleted") and not include_deleted:
            query = query.where(self.model.deleted == False)  # noqa: E712

        return self.session.scalars(query).all()

    def filter(
        self,
        *expressions: BinaryExpression,
    ) -> list[Model]:
        query = select(self.model)
        if expressions:
            query = query.where(*expressions)
        return list(self.session.scalars(query))

class AccessTokenRepository(DatabaseRepository[models.AccessToken]):
    def __init__(self, session: Session) -> None:
        super().__init__(models.AccessToken, session)

    def generate_access_token(self) -> models.AccessToken:
        # Create a new access token
        token = models.AccessToken(
            token=secrets.token_urlsafe(32),
            expires_at=datetime.now() + timedelta(days=365),
        )

        return self.create(token.model_dump())
        
        


class CredentialRepository(DatabaseRepository[models.Credential]):
    def __init__(self, session: Session) -> None:
        super().__init__(models.Credential, session)


class WorkItemRepository(DatabaseRepository[models.WorkItem]):
    def __init__(self, session: Session) -> None:
        super().__init__(models.WorkItem, session)

    def get_next_item(self, queue_id: int):
        """
        Retrieves and locks the next available work item from a specified queue.

        This method selects the next available work item based on the provided
        queue ID, marking the item as locked and updating its status to
        IN_PROGRESS. It ensures atomicity through transaction management and
        prioritizes items based on their creation timestamp.

        Parameters:
            queue_id (int): The ID of the queue to retrieve the next work item from.

        Returns:
            WorkItem | None: The next available work item if found; otherwise, None.

        Raises:
            Exception: Propagates any exceptions that occur during database access or
                    transaction handling, after rolling back any changes.
        """
        try:
            item = self.session.scalars(
                select(models.WorkItem)
                .where(models.WorkItem.workqueue_id == queue_id)
                .where(models.WorkItem.locked == False)  # noqa: E712
                .where(models.WorkItem.status == enums.WorkItemStatus.NEW)
                .order_by(models.WorkItem.created_at)
            ).first()

            if item is None:
                return None

            item.locked = True
            item.status = enums.WorkItemStatus.IN_PROGRESS
            item.updated_at = datetime.now()
            self.session.add(item)
            self.session.commit()

            self.get(item.id)
            return item
        except IntegrityError:
            self.session.rollback()
            raise


class WorkqueueRepository(DatabaseRepository[models.Workqueue]):
    def __init__(self, session: Session) -> None:
        super().__init__(models.Workqueue, session)

    def get_workitem_count(self, workqueue_id: int, status: enums.WorkItemStatus):
        return self.session.exec(
            select(func.count())
            .where(models.WorkItem.workqueue_id == workqueue_id)
            .where(models.WorkItem.status == status)
        ).first()

    def get_workitems_paginated(
        self,
        workqueue_id: int,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
        include_deleted: bool = False,
    ) -> tuple[List[models.WorkItem], int]:
        query = select(models.WorkItem).where(
            models.WorkItem.workqueue_id == workqueue_id
        )

        if search:
            query = query.where(
                or_(
                    models.WorkItem.reference.contains(search),
                    models.WorkItem.status.contains(search),
                )
            )
        query = query.order_by(models.WorkItem.updated_at.desc())
        return [
            self.session.exec(query.offset(skip).limit(limit)).all(),
            self.session.exec(select(func.count()).select_from(query)).first(),
        ]


class ProcessRepository(DatabaseRepository[models.Process]):
    def __init__(self, session: Session) -> None:
        super().__init__(models.Process, session)


class ResourceRepository(DatabaseRepository[models.Resource]):
    def __init__(self, session: Session) -> None:
        super().__init__(models.Resource, session)

    def get_by_fqdn(self, fqdn: str) -> models.Resource | None:
        return self.session.scalars(
            select(models.Resource).where(models.Resource.fqdn == fqdn)
        ).first()

    def get_available_resources(self) -> list[models.Resource]:
        return self.session.scalars(
            select(models.Resource)
            .where(models.Resource.available == True)  # noqa: E712
            .where(models.Resource.deleted == False)  # noqa: E712
        ).all()


class TriggerRepository(DatabaseRepository[models.Trigger]):
    def __init__(self, session: Session) -> None:
        super().__init__(models.Trigger, session)


class SessionRepository(DatabaseRepository[models.Session]):
    def __init__(self, session: Session) -> None:
        super().__init__(models.Session, session)

    def get_by_resource_id(self, resource_id: int) -> models.Session | None:
        """
        Fetches the first active session for a given resource ID.

        This method retrieves the first session that is associated with the provided resource ID and
        whose status is neither COMPLETED nor FAILED. If no such session exists, it returns None.

        Args:
            resource_id (int): The ID of the resource for which to fetch the session.

        Returns:
            models.Session | None: The first active session for the given resource ID, or None if no such session exists.
        """
        return self.session.scalars(
            select(models.Session)
            .where(models.Session.resource_id == resource_id)
            .where(models.Session.status != enums.SessionStatus.COMPLETED)
            .where(models.Session.status != enums.SessionStatus.FAILED)
        ).first()

    def get_new_sessions(self) -> list[models.Session]:
        """
        Fetches all new sessions.

        This method retrieves all sessions whose status is NEW.

        Returns:
            list[models.Session]: A list of all new sessions. Even if they are assigned to a resource.
        """
        return self.session.scalars(
            select(models.Session)
            .where(models.Session.status == enums.SessionStatus.NEW)
            .where(models.Session.deleted == False)  # noqa: E712
            .order_by(models.Session.created_at)
        ).all()

    def get_active_sessions(self) -> list[models.Session]:
        """
        Fetches all active sessions.

        This method retrieves all sessions whose status is either NEW or IN_PROGRESS.

        Returns:
            list[models.Session]: A list of all active sessions. Even if they are assigned to a resource.
        """
        return self.session.scalars(
            select(models.Session)
            .where(models.Session.status == enums.SessionStatus.NEW)
            .where(models.Session.status == enums.SessionStatus.IN_PROGRESS)
            .where(models.Session.deleted == False)  # noqa: E712
            .order_by(models.Session.created_at)
        ).all()

    def create_log(self, log_entry: dict) -> models.SessionLog:
        """
        Creates a new session log entry.

        This method creates a new session log entry for the specified session ID with the provided message.

        Args:
            session_id (int): The ID of the session for which to create the log entry.
            message (str): The message to include in the log entry.

        Returns:
            models.SessionLog: The newly created session log entry.
        """
        log_entry = models.SessionLog(**log_entry)
        self.session.add(log_entry)
        self.session.commit()

        return log_entry

    def get_paginated(
        self,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
        include_deleted: bool = False,
    ) -> tuple[List[models.Session], int]:
        query = select(models.Session)

        if not include_deleted:
            query = query.filter(models.Session.deleted == False)  # noqa: E712

        if search:
            query = query.join(models.Session.process).filter(
                models.Process.name.contains(search)
            )

        # Sort in descending order by default
        query = query.order_by(models.Session.created_at.desc())

        return [
            self.session.exec(query.offset(skip).limit(limit)).all(),
            self.session.exec(select(func.count()).select_from(query)).first(),
        ]


class SessionLogRepository(DatabaseRepository[models.SessionLog]):
    def __init__(self, session: Session) -> None:
        super().__init__(models.SessionLog, session)

    def get_paginated(
        self,
        session_id: int,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
        include_deleted: bool = False,
    ) -> tuple[List[models.SessionLog], int]:
        query = select(models.SessionLog).where(
            models.SessionLog.session_id == session_id
        )

        if search:
            query = query.where(models.SessionLog.message.contains(search))

        return [
            self.session.exec(query.offset(skip).limit(limit)).all(),
            self.session.exec(select(func.count()).select_from(query)).first(),
        ]

    def get_logs_by_session_id(
        self,
        session_id: int,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[models.SessionLog]:
        query = select(models.SessionLog).where(
            models.SessionLog.session_id == session_id
        )

        if search:
            query = query.where(models.SessionLog.message.contains(search))

        logs = self.session.exec(query.offset(skip).limit(limit)).all()
        return logs

    def count_logs_by_session_id(
        self, session_id: int, search: Optional[str] = None
    ) -> int:
        query = select(func.count()).where(models.SessionLog.session_id == session_id)

        if search:
            query = query.where(models.SessionLog.message.contains(search))

        return self.session.exec(query).first()

    def get_logs_by_workitem_id(self, workitem_id: int) -> List[models.SessionLog]:
        return self.session.scalars(
            select(models.SessionLog)
            .where(models.SessionLog.workitem_id == workitem_id)
            .order_by(models.SessionLog.created_at)
        ).all()


class ClientCredentialRepository(DatabaseRepository[models.ClientCredential]):
    def __init__(self, session: Session) -> None:
        super().__init__(models.ClientCredential, session)

    def get_by_client_id(self, client_id: str) -> models.ClientCredential | None:
        return self.session.scalars(
            select(models.ClientCredential).where(
                models.ClientCredential.client_id == client_id
            )
        ).first()
        
    