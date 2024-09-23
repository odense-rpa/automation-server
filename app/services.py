import bcrypt

from typing import Optional

# from sqlmodel import Session
from datetime import datetime, timedelta

from app.api.v1.schemas import PaginatedResponse
from app.database.repository import (
    SessionLogRepository,
    SessionRepository,
    ResourceRepository,
    WorkqueueRepository,
    ClientCredentialRepository
)
from app.database.models import SessionLog, Session, Resource, WorkItem, ClientCredential
from app.enums import SessionStatus

from app.config import settings

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
                if not any(x.status == SessionStatus.IN_PROGRESS and x.resource_id == resource.id for x in self.session_repository.get_active_sessions()):
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




class SessionLogService:
    def __init__(self, session_repository: SessionLogRepository):
        self.repository = session_repository

    def search_logs(
        self,
        session_id: int,
        page: int = 1,
        size: int = 10,
        search: Optional[str] = None,
    ) -> PaginatedResponse[SessionLog]:
        skip = (page - 1) * size
        sessions, total_items = self.repository.get_paginated(
            session_id, search, skip, size
        )

        total_pages = (total_items + size - 1) // size

        response = PaginatedResponse[SessionLog](
            page=page,
            size=size,
            total_items=total_items,
            total_pages=total_pages,
            items=sessions,
        )

        return response

    def get_by_workitem(self, workitem_id: int) -> list[SessionLog]:
        return self.repository.get_logs_by_workitem_id(workitem_id)


class SessionService:
    def __init__(self, session_repository: SessionRepository):
        self.repository = session_repository

    def search_sessions(
        self,
        page: int = 1,
        size: int = 10,
        search: Optional[str] = None,
        include_deleted: bool = False,
    ) -> PaginatedResponse[Session]:
        skip = (page - 1) * size
        sessions, total_items = self.repository.get_paginated(
            search, skip, size, include_deleted
        )
        # total_items = self.repository.count_all(search)
        total_pages = (total_items + size - 1) // size

        response = PaginatedResponse[Session](
            page=page,
            size=size,
            total_items=total_items,
            total_pages=total_pages,
            items=sessions,
        )

        return response

class WorkqueueService:
    def __init__(self, workqueue_repository: WorkqueueRepository):
        self.repository = workqueue_repository
        
    def search_workitems(
        self,
        workqueue_id: int,
        page: int = 1,
        size: int = 10,
        search: Optional[str] = None,
    ) -> PaginatedResponse[WorkItem]:
        skip = (page - 1) * size
        sessions, total_items = self.repository.get_workitems_paginated(
            workqueue_id, search, skip, size
        )

        total_pages = (total_items + size - 1) // size

        response = PaginatedResponse[WorkItem](
            page=page,
            size=size,
            total_items=total_items,
            total_pages=total_pages,
            items=sessions,
        )

        return response
    
class ClientCredentialService():
    def __init__(self, client_credential_repository: ClientCredentialRepository):
        self.repository = client_credential_repository

    def get_by_client_id(self, client_id: str) -> ClientCredential:
        return self.repository.get_by_client_id(client_id)


    def create_client(self, client_id: str, client_secret: str) -> ClientCredential:
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(client_secret.encode("utf-8"), salt + settings.password_salt.encode("utf-8"))
        
        return self.repository.create({
            "client_id": client_id,
            "client_secret": hash.decode("utf-8"),
            "salt": salt.decode("utf-8")
        })

    def validate_client(self, client_id: str, client_secret: str) -> bool:
        client = self.repository.get_by_client_id(client_id)
        
        if client is None:
            return False
        
        # Salted hash comparison
        hash = bcrypt.hashpw(client_secret.encode("utf-8"), client.salt.encode("utf-8") + settings.password_salt.encode("utf-8"))
        
        return hash == client.client_secret.encode("utf-8")

        
        

