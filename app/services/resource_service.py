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
            return self.repository.update(previous, data)

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

        # Here we need to remove any allocated sessions
        sessions = self.session_repository.get_new_sessions()
        for session in (s for s in sessions if s.resource_id == resource.id):
            self.session_repository.update(
                session, {"resource_id": None, "dispatched_at": None}
            )

        return self.repository.update(resource, data)

    def assign_session_to_resource(self, session: Session, resource: Resource):
        data = session.model_dump()

        data["resource_id"] = resource.id
        data["dispatched_at"] = datetime.now()

        self.session_repository.update(session, data)
        self.repository.update(resource, {"available": False})
