"""
Base class for trigger processors.

This module defines the abstract interface that all trigger processors must implement.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict

from app.database.models import Trigger
from app.database.repository import (
    TriggerRepository,
    SessionRepository,
    ResourceRepository,
    WorkqueueRepository,
    ProcessRepository
)
from app.services import SessionService, ResourceService, WorkqueueService
from app.scheduler.validators import validate_parameters, process_trigger_with_validation

logger = logging.getLogger(__name__)


class ProcessingServices:
    """Container for services and repositories needed by trigger processors."""
    
    def __init__(
        self,
        session_service: SessionService,
        resource_service: ResourceService,
        workqueue_service: WorkqueueService,
        trigger_repository: TriggerRepository,
        session_repository: SessionRepository,
        resource_repository: ResourceRepository,
        workqueue_repository: WorkqueueRepository,
        process_repository: ProcessRepository,
    ):
        # Services
        self.session_service = session_service
        self.resource_service = resource_service
        self.workqueue_service = workqueue_service
        
        # Repositories
        self.trigger_repository = trigger_repository
        self.session_repository = session_repository
        self.resource_repository = resource_repository
        self.workqueue_repository = workqueue_repository
        self.process_repository = process_repository


class AbstractTriggerProcessor(ABC):
    """Abstract base class for trigger processors.
    
    This class defines the interface that all trigger processors must implement
    using the Strategy pattern.
    """
    
    def __init__(self, services: ProcessingServices):
        """Initialize the processor with required services.
        
        Args:
            services: Container with all required services
        """
        self.services = services
    
    def process(self, trigger: Trigger, now: datetime) -> bool:
        """Process a trigger with validation.
        
        Args:
            trigger: The trigger to process
            now: Current datetime for time-based processing
            
        Returns:
            True if processing was successful, False otherwise
        """
        try:
            validated_params = validate_parameters(trigger.parameters)
            return process_trigger_with_validation(
                trigger, 
                lambda t, params: self._process_trigger(t, params, now),
                validated_params
            )
        except Exception as e:
            logger.error(f"Error processing trigger {trigger.id}: {e}")
            return False
    
    @abstractmethod
    def _process_trigger(self, trigger: Trigger, validated_params: str, now: datetime) -> bool:
        """Process the specific trigger logic.
        
        This method must be implemented by concrete trigger processors.
        
        Args:
            trigger: The trigger to process
            validated_params: Pre-validated parameters
            now: Current datetime for time-based processing
            
        Returns:
            True if processing was successful, False otherwise
        """
        pass
    
    def _should_trigger_in_current_minute(self, trigger: Trigger, now: datetime) -> bool:
        """Check if a trigger should fire based on last_triggered time.
        
        Args:
            trigger: The trigger to check
            now: Current datetime
            
        Returns:
            True if trigger should fire (hasn't been triggered in current minute), False otherwise
        """
        if trigger.last_triggered is None:
            # Never been triggered, should fire
            return True
        
        # Compare at minute level (ignore seconds and microseconds)
        current_minute = now.replace(second=0, microsecond=0)
        last_triggered_minute = trigger.last_triggered.replace(second=0, microsecond=0)
        
        # Only trigger if it hasn't been triggered in the current minute
        return current_minute != last_triggered_minute
    
    def _create_session(self, trigger: Trigger, validated_params: str, force: bool = False) -> bool:
        """Helper method to create a session for a trigger.
        
        Args:
            trigger: The trigger to create session for
            validated_params: Validated parameters for the session
            force: Whether to force creation even if session exists
            
        Returns:
            True if session was created successfully
        """
        try:
            session = self.services.session_service.create_session(
                trigger.process_id,
                force=force,
                parameters=validated_params
            )
            
            if session:
                # Update last_triggered timestamp after successful session creation
                self.services.trigger_repository.update(
                    trigger, 
                    {"last_triggered": datetime.now()}
                )
                logger.info(f"Created session {session.id} for trigger {trigger.id}")
                return True
            else:
                logger.debug(f"Session already exists for trigger {trigger.id} (force={force})")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create session for trigger {trigger.id}: {e}")
            return False