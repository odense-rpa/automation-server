import requests
import logging
import traceback
from contextlib import contextmanager
from datetime import datetime

from . import automationserver_url
from . import headers

logger = logging.getLogger(__name__)

sessions_base_url = f"{automationserver_url}/sessions"


class SessionLoggingHandler(logging.Handler):
    def __init__(self, session_id: int):
        super().__init__()
        self.session_id = session_id

    def emit(self, record):
        if self.session_id is None:
            return

        try:
            # Create structured audit log data
            log_data = {
                "session_id": self.session_id,
                "message": self.format(record),
                "level": record.levelname,
                "logger_name": record.name,
                "event_timestamp": datetime.fromtimestamp(record.created).isoformat()
            }
            
            # Add source location info
            if hasattr(record, 'module') and record.module:
                log_data["module"] = record.module
            if hasattr(record, 'funcName') and record.funcName:
                log_data["function_name"] = record.funcName
            if hasattr(record, 'lineno') and record.lineno:
                log_data["line_number"] = record.lineno
                
            # Add exception info if present
            if record.exc_info:
                exc_type, exc_value, exc_traceback = record.exc_info
                log_data["exception_type"] = exc_type.__name__ if exc_type else None
                log_data["exception_message"] = str(exc_value) if exc_value else None
                log_data["traceback"] = ''.join(traceback.format_exception(*record.exc_info))
            
            # Make direct API call to new audit logs endpoint
            response = requests.post(f"{automationserver_url}/audit-logs", json=log_data, headers=headers)
            
            if response.status_code != 204:
                response.raise_for_status()
                
        except Exception as e:
            print(f"Failed to send log to audit system: {e}")


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
        update_session_status(session_id=session["id"], status="failed")
        logger.error(e)
    finally:
        if handler is not None:
            logging.getLogger().removeHandler(handler)
            handler = None


def get_pending_session(resource_id: int) -> dict:
    response = requests.get(f"{sessions_base_url}/by_resource_id/{resource_id}", headers=headers)

    if response.status_code == 204:
        return None

    response.raise_for_status()
    return response.json()


def update_session_status(session_id: str, status: str) -> dict:
    allowed_status = ["in progress", "completed", "failed"]

    if status not in allowed_status:
        raise ValueError(f"Status must be one of {allowed_status}")

    response = requests.put(
        f"{sessions_base_url}/{session_id}/status", json={"status": status}, headers=headers
    )
    response.raise_for_status()
    return response.json()


def get_process(session):
    response = requests.get(
        f"{automationserver_url}/processes/{session['process_id']}", headers=headers
    )
    response.raise_for_status()
    return response.json()


def get_credential(credential_id: int) -> dict:
    response = requests.get(
        f"{automationserver_url}/credentials/{credential_id}", headers=headers
    )
    response.raise_for_status()
    return response.json()
