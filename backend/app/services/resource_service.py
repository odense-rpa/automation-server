from datetime import datetime, timedelta

from app.database.repository import SessionRepository, ResourceRepository
from app.database.models import Session, Resource

from app.enums import SessionStatus


class ResourceService:
    def __init__(
        self,
        resource_repository: ResourceRepository,
        session_repository: SessionRepository,
    ):
        self.repository = resource_repository
        self.session_repository = session_repository

    def update_availability(self):
        resources = self.repository.get_all()

        for resource in resources:
            if (
                resource.last_seen < datetime.now() - timedelta(minutes=10)
                and not resource.deleted
                and resource.available
            ):
                # Only detach the resource if there are no in-progress sessions
                if not any(
                    x.status == SessionStatus.IN_PROGRESS
                    and x.resource_id == resource.id
                    for x in self.session_repository.get_active_sessions()
                ):
                    self.detach(resource)

    def enroll(self, fqdn: str, name: str, capabilities: str):
        previous = self.repository.get_by_fqdn(fqdn)

        data = {
            "fqdn": fqdn,
            "name": name,
            "capabilities": capabilities,
            "deleted": False,
            "last_seen": datetime.now(),
            "available": True,
        }

        if previous is not None:
            resource = self.repository.update(previous, data)
            self.flush_sessions(resource)
            return resource

        return self.repository.create(data)

    def keep_alive(self, resource: Resource):
        data = resource.model_dump()

        data["deleted"] = False
        data["last_seen"] = datetime.now()
        data["available"] = True

        return self.repository.update(resource, data)

    def detach(self, resource: Resource):
        data = resource.model_dump()

        data["available"] = False

        self.flush_sessions(resource)

        return self.repository.update(resource, data)

    def flush_sessions(self, resource: Resource):
        """
        Detaches all sessions from the specified resource. 
        If any session is in progress, it will be marked as failed. If any session is new, it will be detached from the resource.
        """
        sessions = self.session_repository.get_active_sessions()
        for session in (s for s in sessions if s.resource_id == resource.id):
            if session.status == SessionStatus.IN_PROGRESS:
                self.session_repository.update(
                    session, {"status": SessionStatus.FAILED, "resource_id": None}
                )

            # Detach the session from the resource
            if session.status == SessionStatus.NEW:
                self.session_repository.update(
                    session, {"resource_id": None, "dispatched_at": None}
                )

    def assign_session_to_resource(self, session: Session, resource: Resource):
        data = session.model_dump()

        data["resource_id"] = resource.id
        data["dispatched_at"] = datetime.now()

        self.session_repository.update(session, data)
        self.repository.update(resource, {"available": False})
