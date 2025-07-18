"""
Core scheduler implementation.

This module contains the refactored AutomationScheduler class using the modular architecture.
"""

import logging
import asyncio
from datetime import datetime

from app.database.session import get_session
from app.database.repository import (
    TriggerRepository,
    SessionRepository,
    ResourceRepository,
    WorkqueueRepository,
    ProcessRepository
)
from app.services import ResourceService, SessionService, WorkqueueService
from app.config import settings
from .trigger_processors import ProcessingServices, TriggerProcessorRegistry
from .dispatcher import ResourceDispatcher

logger = logging.getLogger(__name__)


class AutomationScheduler:
    """Modular scheduler class to manage automation triggers and execution."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self.processor_registry = None
        self.dispatcher = None
    
    async def run_background_task(self):
        """Background task that runs the scheduler in a loop."""
        if not settings.scheduler_enabled:
            logger.info("Scheduler is disabled via configuration")
            return
            
        while True:
            try:
                await self.schedule()
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                # Configurable backoff on error
                await asyncio.sleep(settings.scheduler_error_backoff)
            
            # Configurable sleep interval
            await asyncio.sleep(settings.scheduler_interval)
    
    async def schedule(self):
        """Main scheduling logic using the modular architecture."""
        # Use proper database session management
        with next(get_session()) as session:
            # Initialize repositories
            trigger_repository = TriggerRepository(session)
            session_repository = SessionRepository(session)
            resource_repository = ResourceRepository(session)
            workqueue_repository = WorkqueueRepository(session)
            process_repository = ProcessRepository(session)

            # Initialize services
            resource_service = ResourceService(resource_repository, session_repository)
            session_service = SessionService(session_repository, resource_repository)
            workqueue_service = WorkqueueService(workqueue_repository)
            
            # Initialize processing services container
            processing_services = ProcessingServices(
                session_service=session_service,
                resource_service=resource_service,
                workqueue_service=workqueue_service,
                trigger_repository=trigger_repository,
                session_repository=session_repository,
                resource_repository=resource_repository,
                workqueue_repository=workqueue_repository,
                process_repository=process_repository
            )
            
            # Initialize processor registry and dispatcher
            self.processor_registry = TriggerProcessorRegistry(processing_services)
            self.dispatcher = ResourceDispatcher(resource_service, session_repository)

            # Do housekeeping
            session_service.reschedule_orphaned_sessions()
            session_service.flush_dangling_sessions()

            # Dispatch pending sessions first
            self.dispatcher.dispatch_all_pending()

            # Get current time for trigger evaluation
            now = datetime.now()

            # Process all triggers
            await self._process_triggers(trigger_repository, process_repository, now)

            # Dispatch again for any new sessions created
            self.dispatcher.dispatch_all_pending()

    async def _process_triggers(self, trigger_repository: TriggerRepository, 
                              process_repository: ProcessRepository, now: datetime):
        """Process all enabled triggers.
        
        Args:
            trigger_repository: Repository for trigger operations
            process_repository: Repository for process operations
            now: Current datetime for trigger evaluation
        """
        triggers = trigger_repository.get_all(include_deleted=False)

        for trigger in triggers:
            if not trigger.enabled:
                continue

            # Check if the associated process exists and is not deleted
            process = process_repository.get(trigger.process_id)
            if process is None or process.deleted:
                continue

            try:
                # Get the appropriate processor for this trigger type
                processor = self.processor_registry.get_processor(trigger.type)
                
                # Process the trigger
                success = processor.process(trigger, now)
                
                if not success:
                    logger.warning(f"Failed to process trigger {trigger.id} of type {trigger.type}")
                    
            except ValueError as e:
                logger.error(f"Unsupported trigger type {trigger.type} for trigger {trigger.id}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error processing trigger {trigger.id}: {e}")
                continue


# Global scheduler instance for backward compatibility
scheduler = AutomationScheduler()


async def scheduler_background_task():
    """Backward compatibility function for existing main.py integration."""
    await scheduler.run_background_task()