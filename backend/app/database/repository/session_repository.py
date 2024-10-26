from typing import List, Optional

from sqlalchemy.sql import func
from sqlmodel import Session as SqlSession, select, or_

from app.database.models import Process, Session, SessionLog
import app.enums as enums

from .database_repository import DatabaseRepository


class SessionRepository(DatabaseRepository[Session]):
    def __init__(self, session: SqlSession) -> None:
        super().__init__(Session, session)

    def get_by_resource_id(self, resource_id: int) -> Session | None:
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
            select(Session)
            .where(Session.resource_id == resource_id)
            .where(Session.status != enums.SessionStatus.COMPLETED)
            .where(Session.status != enums.SessionStatus.FAILED)
        ).first()

    def get_new_sessions(self) -> list[Session]:
        """
        Fetches all new sessions.

        This method retrieves all sessions whose status is NEW.

        Returns:
            list[models.Session]: A list of all new sessions. Even if they are assigned to a resource.
        """
        return self.session.scalars(
            select(Session)
            .where(Session.status == enums.SessionStatus.NEW)
            .where(Session.deleted == False)  # noqa: E712
            .order_by(Session.created_at)
        ).all()

    def get_active_sessions(self) -> list[Session]:
        """
        Fetches all active sessions.

        This method retrieves all sessions whose status is either NEW or IN_PROGRESS.

        Returns:
            list[models.Session]: A list of all active sessions. Even if they are assigned to a resource.
        """
        return self.session.scalars(
            select(Session)
            .where(
                or_(
                    Session.status == enums.SessionStatus.NEW,
                    Session.status == enums.SessionStatus.IN_PROGRESS,
                )
            )
            .where(Session.deleted == False)  # noqa: E712
            .order_by(Session.created_at)
        ).all()

    def create_log(self, log_entry: dict) -> SessionLog:
        """
        Creates a new session log entry.

        This method creates a new session log entry for the specified session ID with the provided message.

        Args:
            session_id (int): The ID of the session for which to create the log entry.
            message (str): The message to include in the log entry.

        Returns:
            models.SessionLog: The newly created session log entry.
        """
        log_entry = SessionLog(**log_entry)
        self.session.add(log_entry)
        self.session.commit()

        return log_entry

    def get_paginated(
        self,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
        include_deleted: bool = False,
    ) -> tuple[List[Session], int]:
        query = select(Session)

        if not include_deleted:
            query = query.filter(Session.deleted == False)  # noqa: E712

        if search:
            query = query.join(Session.process).filter(Process.name.contains(search))

        # Sort in descending order by default
        query = query.order_by(Session.created_at.desc())

        return [
            self.session.exec(query.offset(skip).limit(limit)).all(),
            self.session.exec(select(func.count()).select_from(query)).first(),
        ]
