import logging
import re
from datetime import datetime, timedelta
from croniter import croniter

from app.database.session import get_session
from app.database.repository import (
    TriggerRepository,
    SessionRepository,
    ResourceRepository,
)
from app.services import ResourceService, SessionService
from app.enums import SessionStatus

from fastapi import Depends

logger = logging.getLogger(__name__)

last_run = None


async def schedule():
    with next(get_session()) as session:
        global last_run

        trigger_repository = TriggerRepository(session)
        session_repository = SessionRepository(session)
        resource_repository = ResourceRepository(session)
        resource_service = ResourceService(resource_repository, session_repository)
        session_service = SessionService(session_repository, resource_repository)

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

        sessions = session_repository.get_active_sessions()

        for trigger in triggers:
            if trigger.enabled is False:
                continue

            if trigger.type == "cron":
                if croniter.match(trigger.cron, now):
                    logger.info(f"Triggering cron trigger {trigger.id}")
                    new_session(trigger.process_id, session_repository)

            if trigger.type == "date":
                if trigger.date <= now:
                    logger.info(f"Triggering date trigger {trigger.id}")
                    new_session(trigger.process_id, session_repository)
                    trigger_repository.update(
                        trigger, {"enabled": False, "deleted": True}
                    )

            if trigger.type == "workqueue":
                workqueue = trigger.workqueue

                if workqueue is None:
                    logger.error(f"Workqueue {trigger.workqueue_id} does not exist")
                    continue

                if workqueue.enabled is False:
                    continue

                if trigger.workqueue_id not in sessions:
                    logger.info(f"Triggering workqueue trigger {trigger.id}")

        # Dispatch again to assign resources to the new sessions
        dispatch(session_repository, resource_repository, resource_service)


def new_session(process_id: int, session_repository: SessionRepository):
    sessions = session_repository.get_new_sessions()

    # If there is a new or in progress session in the sessions objects, return
    if any(session.process_id == process_id for session in sessions):
        return

    # Create a new session
    session = session_repository.create(
        {
            "process_id": process_id,
            "status": SessionStatus.NEW,
            "deleted": False,
            "dispatched_at": None,
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
