from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.sql import func, case
from sqlalchemy.types import String
from sqlmodel import Session as SqlSession, cast, select, or_

from app.database.models import Incident, Process, Session, AuditLog
import app.enums as enums

from .database_repository import DatabaseRepository, AbstractRepository


class AbstractSessionRepository(AbstractRepository[Session]):
    def get_by_resource_id(self, resource_id: int) -> Session | None:
        raise NotImplementedError

    def get_new_sessions(self) -> list[Session]:
        raise NotImplementedError

    def get_active_sessions(self) -> list[Session]:
        raise NotImplementedError

    def get_failed_without_incident(self, max_age_days: int = 14) -> list[Session]:
        raise NotImplementedError

    def create_log(self, log_entry: dict) -> AuditLog:
        raise NotImplementedError

    def get_paginated(
        self,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
        include_deleted: bool = False,
    ) -> tuple[List[Session], int]:
        raise NotImplementedError

    def get_process_activity_summary(self, since: datetime) -> list[dict]:
        raise NotImplementedError


class SessionRepository(AbstractSessionRepository, DatabaseRepository[Session]):
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

    def get_failed_without_incident(self, max_age_days: int = 14) -> list[Session]:
        """Return failed, non-deleted sessions without an incident, created within the last max_age_days days."""
        cutoff = datetime.now() - timedelta(days=max_age_days)
        return list(self.session.scalars(
            select(Session)
            .outerjoin(Incident, Incident.session_id == Session.id)
            .where(Session.status == enums.SessionStatus.FAILED)
            .where(Session.deleted == False)  # noqa: E712
            .where(Incident.id.is_(None))
            .where(Session.created_at >= cutoff)
        ).all())

    def create_log(self, log_entry: dict) -> AuditLog:
        """
        Creates a new session log entry.

        This method creates a new session log entry for the specified session ID with the provided message.

        Args:
            session_id (int): The ID of the session for which to create the log entry.
            message (str): The message to include in the log entry.

        Returns:
            models.AuditLog: The newly created session log entry.
        """
        log_entry = AuditLog(**log_entry)
        self.session.add(log_entry)
        self.session.commit()

        return log_entry

    def get_process_activity_summary(self, since: datetime) -> list[dict]:
        rows = self.session.exec(
            select(
                Session.process_id,
                Process.name,
                func.count(case((Session.status == enums.SessionStatus.COMPLETED, 1))).label("completed"),
                func.count(case((Session.status == enums.SessionStatus.FAILED, 1))).label("failed"),
                func.count(case((Session.status == enums.SessionStatus.IN_PROGRESS, 1))).label("in_progress"),
                func.count(case((Session.status == enums.SessionStatus.NEW, 1))).label("new"),
                func.max(Session.created_at).label("last_activity"),
            )
            .join(Process, Session.process_id == Process.id)
            .where(Session.deleted == False)  # noqa: E712
            .where(
                or_(
                    Session.created_at >= since,
                    Session.status.in_([enums.SessionStatus.NEW, enums.SessionStatus.IN_PROGRESS]),
                )
            )
            .group_by(Session.process_id, Process.name)
            .order_by(func.max(Session.created_at).desc())
        ).all()

        return [
            {
                "process_id": process_id,
                "process_name": name,
                "completed": completed,
                "failed": failed,
                "in_progress": in_progress,
                "new": new,
                "last_activity": last_activity,
            }
            for process_id, name, completed, failed, in_progress, new, last_activity in rows
        ]

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
            query = query.join(Session.process).filter(
                or_(
                    Process.name.ilike(f"%{search}%"),
                    cast(Session.status, String).ilike(f"%{search}%"),
                )
            )

        # Sort in descending order by default
        query = query.order_by(Session.id.desc())

        count_query = select(func.count()).select_from(Session)
        if query.whereclause is not None:
            if search: # If search is active, the join to Process is active
                count_query = count_query.join(Session.process)

            count_query = count_query.where(query.whereclause)
        
        total_count = self.session.exec(count_query).first()

        return (
            list(self.session.exec(query.offset(skip).limit(limit)).all()),
            total_count,
        )
