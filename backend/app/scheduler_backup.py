import logging
import re
import asyncio
from datetime import datetime
from croniter import croniter

from app.database.session import get_session
from app.database.repository import (
    TriggerRepository,
    SessionRepository,
    ResourceRepository,
    WorkqueueRepository,
    ProcessRepository
)
from app.services import ResourceService, SessionService, WorkqueueService
from app.enums import SessionStatus
from app.config import settings

logger = logging.getLogger(__name__)


def validate_parameters(parameters: str) -> str:
    """Simple parameter validation for trigger parameters.
    
    Args:
        parameters: Raw parameter string from trigger
        
    Returns:
        Cleaned parameter string
        
    Raises:
        ValueError: If parameters are too long
    """
    if not parameters:
        return ""
    
    # Simple length check for basic protection
    if len(parameters) > settings.scheduler_max_parameter_length:
        raise ValueError(f"Parameters too long (max {settings.scheduler_max_parameter_length} characters)")
    
    return parameters.strip()


def validate_cron_expression(cron_expr: str) -> str:
    """Simple cron expression validation.
    
    Args:
        cron_expr: Cron expression string
        
    Returns:
        Validated cron expression
        
    Raises:
        ValueError: If cron expression is invalid
    """
    if not cron_expr or not cron_expr.strip():
        raise ValueError("Cron expression cannot be empty")
    
    cron_expr = cron_expr.strip()
    
    try:
        # Let croniter handle all validation
        croniter(cron_expr)
    except Exception as e:
        raise ValueError(f"Invalid cron expression: {e}")
    
    return cron_expr


def process_trigger_with_validation(trigger, session_repository, trigger_logic_func):
    """Helper function to reduce code duplication in trigger processing.
    
    Args:
        trigger: The trigger object to process
        session_repository: Session repository for creating sessions
        trigger_logic_func: Function that contains the specific trigger logic
        
    Returns:
        bool: True if trigger was processed successfully
    """
    try:
        validated_params = validate_parameters(trigger.parameters)
        return trigger_logic_func(trigger, session_repository, validated_params)
    except ValueError as e:
        logger.error(f"Invalid trigger {trigger.id}: {e}")
        return False


def calculate_required_sessions(pending_items, scale_threshold):
    """Calculate how many sessions are needed based on pending items.
    
    Args:
        pending_items: Number of pending work items
        scale_threshold: Items per session threshold
        
    Returns:
        int: Number of sessions required (minimum 1)
    """
    if pending_items == 0:
        return 0
    
    required = pending_items // max(scale_threshold, 1)
    return max(1, required)


def should_scale_up(active_sessions, required_sessions, resource_limit):
    """Check if we should scale up based on current and required sessions.
    
    Args:
        active_sessions: List of currently active sessions
        required_sessions: Number of sessions we need
        resource_limit: Maximum allowed sessions for this trigger
        
    Returns:
        bool: True if we should create a new session
    """
    if required_sessions == 0:
        return False
    
    # Don't exceed the resource limit
    capped_required = min(required_sessions, resource_limit)
    return len(active_sessions) < capped_required


class AutomationScheduler:
    """Simple scheduler class to manage automation triggers and execution."""
    
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
        """Main scheduling logic."""
        # Use proper database session management
        with next(get_session()) as session:
            trigger_repository = TriggerRepository(session)
            session_repository = SessionRepository(session)
            resource_repository = ResourceRepository(session)
            resource_service = ResourceService(resource_repository, session_repository)
            session_service = SessionService(session_repository, resource_repository)
            workqueue_repository = WorkqueueRepository(session)
            workqueue_service = WorkqueueService(workqueue_repository)
            process_repository = ProcessRepository(session)

            # Do some housekeeping
            session_service.reschedule_orphaned_sessions()
            session_service.flush_dangling_sessions()

            # We dispatch first to get any old sessions a chance to get a resource before the triggers are checked
            dispatch(session_repository, resource_repository, resource_service)

            now = datetime.now()

            triggers = trigger_repository.get_all(include_deleted=False)

            for trigger in triggers:
                if trigger.enabled is False:
                    continue

                process = process_repository.get(trigger.process_id)
                
                if process is None or process.deleted:
                    continue

                if trigger.type == "cron":
                    def cron_logic(trigger, session_repository, validated_params):
                        validated_cron = validate_cron_expression(trigger.cron)
                        if croniter.match(validated_cron, now):
                            logger.info(f"Triggering cron trigger {trigger.id}")
                            new_session(trigger.process_id, session_repository, parameters=validated_params)
                        return True
                    
                    if not process_trigger_with_validation(trigger, session_repository, cron_logic):
                        continue

                if trigger.type == "date":
                    def date_logic(trigger, session_repository, validated_params):
                        if trigger.date <= now:
                            logger.info(f"Triggering date trigger {trigger.id}")
                            new_session(trigger.process_id, session_repository, parameters=validated_params)
                            trigger_repository.update(trigger, {"enabled": False, "deleted": True})
                        return True
                    
                    if not process_trigger_with_validation(trigger, session_repository, date_logic):
                        continue

                if trigger.type == "workqueue":
                    def workqueue_logic(trigger, session_repository, validated_params):
                        workqueue = workqueue_repository.get(trigger.workqueue_id)
                        
                        if workqueue is None:
                            logger.error(f"Workqueue {trigger.workqueue_id} does not exist")
                            return True  # Continue processing other triggers
                        
                        if not workqueue.enabled:
                            return True  # Skip disabled workqueues
                        
                        # Check for pending work items
                        pending_items = workqueue_service.count_pending_items(trigger.workqueue_id)
                        
                        # Calculate how many sessions we need
                        required_sessions = calculate_required_sessions(
                            pending_items, trigger.workqueue_scale_up_threshold
                        )
                        
                        if required_sessions == 0:
                            return True  # No work to do
                        
                        # Check current active sessions for this process
                        active_sessions = [
                            session for session in session_repository.get_active_sessions()
                            if session.process_id == trigger.process_id
                        ]
                        
                        # Decide if we should scale up
                        if should_scale_up(active_sessions, required_sessions, trigger.workqueue_resource_limit):
                            logger.info(f"Triggering workqueue trigger {trigger.id}. "
                                      f"Required: {min(required_sessions, trigger.workqueue_resource_limit)}, "
                                      f"Active: {len(active_sessions)}")
                            
                            # Check if resources are available
                            resources = resource_repository.get_available_resources()
                            if find_best_resource(process.requirements, resources) is not None:
                                # Only trigger one session per tick to allow other processes to scale
                                new_session(trigger.process_id, session_repository, 
                                           force=True, parameters=validated_params)
                        
                        return True
                    
                    if not process_trigger_with_validation(trigger, session_repository, workqueue_logic):
                        continue

            # Dispatch again to assign resources to the new sessions
            dispatch(session_repository, resource_repository, resource_service)


# Global scheduler instance
scheduler = AutomationScheduler()


async def scheduler_background_task():
    """Backward compatibility function for existing main.py integration."""
    await scheduler.run_background_task()


def new_session(
    process_id: int,
    session_repository: SessionRepository,
    force=False,
    parameters: str = None,
):
    sessions = session_repository.get_new_sessions()

    # If there is a new or in progress session in the sessions objects, return
    if any(session.process_id == process_id for session in sessions) and not force:
        return

    # Create a new session
    session = session_repository.create(
        {
            "process_id": process_id,
            "status": SessionStatus.NEW,
            "deleted": False,
            "dispatched_at": None,
            "parameters": parameters,
        }
    )

    return session


def dispatch(
    session_repository: SessionRepository,
    resource_repository: ResourceRepository,
    resource_service: ResourceService,
):
    resource_service.update_availability()

    sessions = session_repository.get_new_sessions()

    sessions = sorted(
        [
            session
            for session in sessions
            if session.status == SessionStatus.NEW and session.resource_id is None
        ],
        key=lambda session: session.created_at,
        reverse=False,
    )

    for session in sessions:
        resources = resource_repository.get_available_resources()
        requirements = session.process.requirements

        best_resource = find_best_resource(requirements, resources)

        if best_resource is None:
            logger.info(f"No available resources for session {session.id}")
            continue

        resource_service.assign_session_to_resource(session, best_resource)

        logger.info(f"Dispatched session {session.id} to resource {best_resource.id}")


def parse_capabilities_or_requirements(string):
    # Split by space or comma
    return set(re.split(r"[ ,]+", string.strip()))


def find_best_resource(requirements, resources):
    session_requirements = parse_capabilities_or_requirements(requirements)
    best_resource = None
    least_capabilities = float("inf")

    for resource in resources:
        resource_capabilities = parse_capabilities_or_requirements(
            resource.capabilities
        )
        if session_requirements.issubset(resource_capabilities):
            if len(resource_capabilities) < least_capabilities:
                best_resource = resource
                least_capabilities = len(resource_capabilities)

    return best_resource
