import logging
import re
import asyncio
from datetime import datetime, timedelta
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

logger = logging.getLogger(__name__)

last_run = None


async def scheduler_background_task():
    while True:
        # Run the scheduler
        await schedule()

        # Sleep for 10 seconds before the next iteration
        await asyncio.sleep(10)


async def schedule():
    with next(get_session()) as session:
        global last_run
        
        
        
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
        if last_run and now - last_run < timedelta(minutes=1):
            return

        last_run = now

        triggers = trigger_repository.get_all(include_deleted=False)

        for trigger in triggers:
            if trigger.enabled is False:
                continue

            process = process_repository.get(trigger.process_id)
            
            if process is None or process.deleted:
                continue

            if trigger.type == "cron":
                if croniter.match(trigger.cron, now):
                    logger.info(f"Triggering cron trigger {trigger.id}")
                    new_session(
                        trigger.process_id,
                        session_repository,
                        parameters=trigger.parameters,
                    )

            if trigger.type == "date":
                if trigger.date <= now:
                    logger.info(f"Triggering date trigger {trigger.id}")
                    new_session(
                        trigger.process_id,
                        session_repository,
                        parameters=trigger.parameters,
                    )
                    trigger_repository.update(
                        trigger, {"enabled": False, "deleted": True}
                    )

            if trigger.type == "workqueue":
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
                            parameters=trigger.parameters,
                        )

        # Dispatch again to assign resources to the new sessions
        dispatch(session_repository, resource_repository, resource_service)


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
