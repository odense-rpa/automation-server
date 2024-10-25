import requests
import logging

from contextlib import contextmanager

from . import automationserver_url
from . import headers

logger = logging.getLogger(__name__)

base_url = f"{automationserver_url}/sessions"


class SessionLoggingHandler(logging.Handler):
    def __init__(self, session_id: int):
        super().__init__()
        self.session_id = session_id

    def emit(self, record):
        log_entry = self.format(record)

        if self.session_id is None:
            return

        try:
            add_log_message(session_id=self.session_id, message=log_entry)
        except Exception as e:
            print(f"Failed to send log to session: {e}")


@contextmanager
def acquire_session(resource_id: int):
    handler = None

    session = get_pending_session(resource_id=resource_id)
    try:
        if session is not None:
            update_session_status(session_id=session["id"], status="in progress")
            handler = SessionLoggingHandler(session_id=session["id"])
            logging.getLogger().addHandler(handler)

        yield session

        if session is not None:
            logger.info("Completing session.")
            update_session_status(session_id=session["id"], status="completed")

    except Exception as e:
        # update_session_status(session_id=session["id"], status="failed")
        logger.error(e)
    finally:
        if handler is not None:
            logging.getLogger().removeHandler(handler)
            handler = None


def get_pending_session(resource_id: int) -> dict:
    response = requests.get(f"{base_url}/by_resource_id/{resource_id}", headers=headers)

    if response.status_code == 204:
        return None

    response.raise_for_status()
    return response.json()


def update_session_status(session_id: str, status: str) -> dict:
    allowed_status = ["in progress", "completed", "failed"]

    if status not in allowed_status:
        raise ValueError(f"Status must be one of {allowed_status}")

    response = requests.put(
        f"{base_url}/{session_id}/status", json={"status": status}, headers=headers
    )
    response.raise_for_status()
    return response.json()


def get_process(session):
    response = requests.get(
        f"{automationserver_url}/processes/{session['process_id']}", headers=headers
    )
    response.raise_for_status()
    return response.json()


def add_log_message(session_id: int, message: str, workqueue_id=None) -> dict:
    json = {"message": message}
    if workqueue_id is not None:
        json["workqueue_id"] = workqueue_id

    response = requests.post(f"{base_url}/{session_id}/log", json=json, headers=headers)

    if response.status_code != 204:
        response.raise_for_status()
