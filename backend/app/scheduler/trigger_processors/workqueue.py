"""
Workqueue trigger processor.

This module implements the trigger processor for workqueue-based scheduling.
"""

import logging
from datetime import datetime
from typing import List

from app.database.models import Trigger
from app.scheduler.utils import calculate_required_sessions, should_scale_up, find_best_resource
from .base import AbstractTriggerProcessor

logger = logging.getLogger(__name__)


class WorkqueueTriggerProcessor(AbstractTriggerProcessor):
    """Processor for workqueue-based triggers."""
    
    def _process_trigger(self, trigger: Trigger, validated_params: str, now: datetime) -> bool:
        """Process a workqueue trigger.
        
        Args:
            trigger: The workqueue trigger to process
            validated_params: Pre-validated parameters
            now: Current datetime (not used for workqueue triggers)
            
        Returns:
            True if processing was successful
        """
        try:
            # Get the workqueue
            workqueue = self._get_workqueue(trigger)
            if not workqueue:
                return True  # Continue processing other triggers
            
            if not workqueue.enabled:
                return True  # Skip disabled workqueues
            
            # Check for pending work items
            pending_items = self.services.workqueue_service.count_pending_items(trigger.workqueue_id)
            
            # Calculate how many sessions we need
            required_sessions = calculate_required_sessions(
                pending_items, trigger.workqueue_scale_up_threshold
            )
            
            if required_sessions == 0:
                return True  # No work to do
            
            # Check current active sessions for this process
            active_sessions = self._get_active_sessions_for_process(trigger.process_id)
            
            # Decide if we should scale up
            if should_scale_up(active_sessions, required_sessions, trigger.workqueue_resource_limit):
                logger.info(
                    f"Triggering workqueue trigger {trigger.id}. "
                    f"Required: {min(required_sessions, trigger.workqueue_resource_limit)}, "
                    f"Active: {len(active_sessions)}"
                )
                
                # Check if resources are available before creating session
                if self._are_resources_available(trigger):
                    # Only trigger one session per tick to allow other processes to scale
                    return self._create_session(trigger, validated_params, force=True)
                else:
                    logger.debug(f"No resources available for workqueue trigger {trigger.id}")
                    return True
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing workqueue trigger {trigger.id}: {e}")
            return False
    
    def _get_workqueue(self, trigger: Trigger):
        """Get the workqueue for a trigger.
        
        Args:
            trigger: The trigger to get workqueue for
            
        Returns:
            Workqueue object or None if not found
        """
        try:
            if not trigger.workqueue_id:
                logger.error(f"Workqueue trigger {trigger.id} has no workqueue_id")
                return None
                
            workqueue = self.services.workqueue_repository.get(trigger.workqueue_id)
            
            if workqueue is None:
                logger.error(f"Workqueue {trigger.workqueue_id} does not exist")
                return None
                
            return workqueue
            
        except Exception as e:
            logger.error(f"Error getting workqueue {trigger.workqueue_id}: {e}")
            return None
    
    def _get_active_sessions_for_process(self, process_id: int) -> List:
        """Get active sessions for a specific process.
        
        Args:
            process_id: The process ID to filter by
            
        Returns:
            List of active sessions for the process
        """
        try:
            active_sessions = self.services.session_repository.get_active_sessions()
            return [
                session for session in active_sessions
                if session.process_id == process_id
            ]
            
        except Exception as e:
            logger.error(f"Error getting active sessions for process {process_id}: {e}")
            return []
    
    def _are_resources_available(self, trigger: Trigger) -> bool:
        """Check if resources are available for a trigger.
        
        Args:
            trigger: The trigger to check resources for
            
        Returns:
            True if resources are available
        """
        try:
            # Get the process to check its requirements
            process = self.services.process_repository.get(trigger.process_id)
            if process is None:
                logger.error(f"Process {trigger.process_id} not found for trigger {trigger.id}")
                return False
            
            # Get available resources
            available_resources = self.services.resource_repository.get_available_resources()
            
            # Check if any resource can satisfy the requirements
            best_resource = find_best_resource(process.requirements, available_resources)
            
            return best_resource is not None
            
        except Exception as e:
            logger.error(f"Error checking resources for trigger {trigger.id}: {e}")
            return False