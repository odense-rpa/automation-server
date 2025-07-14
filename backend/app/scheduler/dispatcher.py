"""
Resource dispatcher for scheduler operations.

This module handles complex session-to-resource dispatching logic for the scheduler.
"""

import logging
from datetime import datetime
from app.services import ResourceService
from app.database.repository import SessionRepository
from app.database.models import Session, Resource
from app.enums import SessionStatus

logger = logging.getLogger(__name__)


class ResourceDispatcher:
    """Handles dispatching of pending sessions to available resources."""
    
    def __init__(self, resource_service: ResourceService, session_repository: SessionRepository):
        """Initialize the dispatcher with required services.
        
        Args:
            resource_service: ResourceService instance for basic resource operations
            session_repository: SessionRepository for session operations
        """
        self.resource_service = resource_service
        self.session_repository = session_repository
    
    def dispatch_all_pending(self):
        """Dispatch all pending sessions to available resources.
        
        This method finds all NEW sessions without resources and attempts to
        match them with available resources based on their requirements.
        """
        try:
            self._dispatch_pending_sessions()
            logger.debug("Successfully dispatched pending sessions")
        except Exception as e:
            logger.error(f"Error dispatching pending sessions: {e}")
            raise
    
    def _dispatch_pending_sessions(self):
        """Internal method to handle the complex dispatching logic."""
        # Import here to avoid circular imports
        from app.scheduler.utils import find_best_resource
        
        # Update resource availability first
        self.resource_service.update_availability()

        # Get all new sessions that need resources
        sessions = self.session_repository.get_new_sessions()

        # Filter to only sessions that are NEW and don't have resources
        pending_sessions = [
            session
            for session in sessions
            if session.status == SessionStatus.NEW and session.resource_id is None
        ]

        # Sort by creation time (FIFO)
        pending_sessions.sort(key=lambda s: s.created_at)

        # Process each pending session
        for session in pending_sessions:
            available_resources = self.resource_service.repository.get_available_resources()
            requirements = session.process.requirements if session.process else ""

            best_resource = find_best_resource(requirements, available_resources)

            if best_resource is None:
                # Log that no resources are available (but don't fail the session)
                continue

            # Assign the session to the best resource
            self._assign_session_to_resource(session, best_resource)
    
    def _assign_session_to_resource(self, session: Session, resource: Resource):
        """Assign a session to a resource and update both entities.
        
        Args:
            session: Session to assign
            resource: Resource to assign to
        """
        data = session.model_dump()

        data["resource_id"] = resource.id
        data["dispatched_at"] = datetime.now()

        self.session_repository.update(session, data)
        self.resource_service.repository.update(resource, {"available": False})