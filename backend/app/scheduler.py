import logging
import re
import asyncio
from datetime import datetime
from croniter import croniter
import shlex

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
    """Validate and sanitize trigger parameters to prevent injection attacks.
    
    Args:
        parameters: Raw parameter string from trigger
        
    Returns:
        Sanitized parameter string
        
    Raises:
        ValueError: If parameters contain dangerous characters
    """
    if not parameters:
        return ""
    
    # Remove any null bytes
    parameters = parameters.replace('\x00', '')
    
    # Check for dangerous shell metacharacters
    dangerous_chars = ['|', '&', ';', '>', '<', '`', '$', '(', ')', '{', '}', '[', ']', '*', '?', '!', '~']
    for char in dangerous_chars:
        if char in parameters:
            raise ValueError(f"Invalid character '{char}' in parameters")
    
    # Check for dangerous command sequences
    dangerous_sequences = ['rm ', 'del ', 'format ', 'shutdown', 'reboot', 'sudo', 'su ', 'chmod', 'chown']
    params_lower = parameters.lower()
    for seq in dangerous_sequences:
        if seq in params_lower:
            raise ValueError(f"Dangerous command sequence '{seq}' detected in parameters")
    
    # Ensure parameters can be safely parsed as shell arguments
    try:
        shlex.split(parameters)
    except ValueError as e:
        raise ValueError(f"Invalid parameter format: {e}")
    
    # Additional length check
    if len(parameters) > settings.scheduler_max_parameter_length:
        raise ValueError(f"Parameters too long (max {settings.scheduler_max_parameter_length} characters)")
    
    return parameters.strip()


def validate_cron_expression(cron_expr: str) -> str:
    """Validate cron expression format.
    
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
        # Test if croniter can parse it
        croniter(cron_expr)
    except Exception as e:
        raise ValueError(f"Invalid cron expression: {e}")
    
    # Additional validation - ensure it has correct number of fields
    fields = cron_expr.split()
    if len(fields) not in [5, 6]:  # Standard cron (5 fields) or with seconds (6 fields)
        raise ValueError("Cron expression must have 5 or 6 fields")
    
    return cron_expr


class AutomationScheduler:
    """Simple scheduler class to manage automation triggers and execution."""
    
    def __init__(self):
        pass
    
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
        # Use the session generator properly
        session_gen = get_session()
        session = next(session_gen)
        
        try:
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
                    try:
                        # Validate cron expression
                        validated_cron = validate_cron_expression(trigger.cron)
                        validated_params = validate_parameters(trigger.parameters)
                        
                        if croniter.match(validated_cron, now):
                            logger.info(f"Triggering cron trigger {trigger.id}")
                            new_session(
                                trigger.process_id,
                                session_repository,
                                parameters=validated_params,
                            )
                    except ValueError as e:
                        logger.error(f"Invalid cron trigger {trigger.id}: {e}")
                        continue

                if trigger.type == "date":
                    try:
                        validated_params = validate_parameters(trigger.parameters)
                        
                        if trigger.date <= now:
                            logger.info(f"Triggering date trigger {trigger.id}")
                            new_session(
                                trigger.process_id,
                                session_repository,
                                parameters=validated_params,
                            )
                            trigger_repository.update(
                                trigger, {"enabled": False, "deleted": True}
                            )
                    except ValueError as e:
                        logger.error(f"Invalid date trigger {trigger.id}: {e}")
                        continue

                if trigger.type == "workqueue":
                    try:
                        validated_params = validate_parameters(trigger.parameters)
                        
                        workqueue = workqueue_repository.get(trigger.workqueue_id)

                        if workqueue is None:
                            logger.error(f"Workqueue {trigger.workqueue_id} does not exist")
                            continue

                        if workqueue.enabled is False:
                            continue

                        # Check if the workqueue has pending items
                        pending_items = workqueue_service.count_pending_items(
                            trigger.workqueue_id
                        )

                        if pending_items == 0:
                            continue

                        # Check how many sessions are running of process_id
                        active_sessions = [
                            session
                            for session in session_repository.get_active_sessions()
                            if session.process_id == trigger.process_id
                        ]

                        required_sessions = pending_items // max(
                            trigger.workqueue_scale_up_threshold, 1
                        )
                        
                        if required_sessions == 0:
                            required_sessions = 1

                        if required_sessions > trigger.workqueue_resource_limit:
                            required_sessions = trigger.workqueue_resource_limit

                        if len(active_sessions) < required_sessions:
                            logger.info(
                                f"Triggering workqueue trigger {trigger.id}. Required sessions: {required_sessions}, Active sessions: {len(active_sessions)}"
                            )

                            # Check if there are available resources
                            resources = resource_repository.get_available_resources()

                            if find_best_resource(process.requirements, resources) is not None:
                                # Only trigger a single session pr tick. This allows other processes to scale up
                                new_session(
                                    trigger.process_id,
                                    session_repository,
                                    force=True,
                                    parameters=validated_params,
                                )
                    except ValueError as e:
                        logger.error(f"Invalid workqueue trigger {trigger.id}: {e}")
                        continue

            # Dispatch again to assign resources to the new sessions
            dispatch(session_repository, resource_repository, resource_service)
            
        except Exception as e:
            logger.error(f"Error in scheduler: {e}")
            raise
        finally:
            # Properly close the session generator
            try:
                next(session_gen)
            except StopIteration:
                pass  # Normal end of generator


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
