import logging
import os
import pathlib
import platform
import socket
import threading
import time

from requests.exceptions import ConnectionError, RequestException

from automationclient import (
    automationserver_token,
    automationserver_url,
    resources,
    sessions,
)
from errors import SessionError
from runners import python

HEALTH_FILE = pathlib.Path("/tmp/worker.health")

# Container log. ATS_LOG_LEVEL=DEBUG also shows the exact commands being run;
# the session audit log only ever receives INFO and above.
logging.basicConfig(
    level=os.getenv("ATS_LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

capabilities = f"python playwright {platform.system()} {os.getenv('ATS_CAPABILITIES') or ""}".lower().strip()

stop_ping_thread = threading.Event()

def ping_resource(resource_id: int) -> None:
    """
    Ping the resource to keep it alive.
    """
    while not stop_ping_thread.is_set():
        try:
            resources.ping_resource(resource_id)
            HEALTH_FILE.touch()
            time.sleep(120)
        except RequestException as e:
            # Any request error (not only connection errors) must not kill the thread
            logger.warning("Failed to ping resource %s (%s), retrying in 5 seconds", resource_id, e)
            time.sleep(5)

if __name__ == "__main__":
    ping_thread = None

    logger.info(f"Starting worker with capabilities: '{capabilities}'")
    try:
        while True:
            try:
                with resources.acquire_resource(
                    fqdn=socket.getfqdn(),
                    name=socket.gethostname(),
                    capabilities=capabilities,
                ) as resource:
                    
                    if ping_thread is None or not ping_thread.is_alive():
                        ping_thread = threading.Thread(target=ping_resource, args=(resource["id"],))
                        ping_thread.start()
                    
                    while True:
                        with sessions.acquire_session(
                            resource_id=resource["id"]
                        ) as session:
                            if session is None:
                                HEALTH_FILE.touch()
                                time.sleep(10)
                                continue

                            process = sessions.get_process(session)

                            if process is None:
                                raise SessionError(
                                    f"Process {session['process_id']} not found"
                                )

                            params_info = f" with parameters: {session['parameters']}" if session.get('parameters') else " with no parameters"
                            logger.info(
                                f"Running {process['name']} (type: {process['target_type']}){params_info}"
                            )

                            # TODO: Get the credentials associated with GIT.
                            username = None
                            token = None
                            if process["target_credentials_id"] is not None and process["target_credentials_id"] != 0:
                                credentials = sessions.get_credential(
                                    process["target_credentials_id"]
                                )
                                logger.info(f"Using credentials: {credentials["name"]}")
                                username = credentials["username"]
                                token = credentials["password"]

                            if process["target_type"] == "python":
                                python.run_python(
                                    repo_url=process["target_source"],
                                    username=username,
                                    token=token,
                                    git_options=process.get("git_options"),
                                    script_env={
                                        "ATS_URL": automationserver_url,
                                        "ATS_TOKEN": automationserver_token,
                                        "ATS_SESSION": f"{session['id']}",
                                        "ATS_RESOURCE": f"{resource['id']}",
                                        "ATS_PROCESS": f"{process['id']}",
                                    },
                                    parameters=session["parameters"],
                                )
                            else:
                                raise SessionError(
                                    f"target_type '{process['target_type']}' is not supported by this worker"
                                )

                            resources.ping_resource(resource["id"])
            except ConnectionError:
                logger.error(
                    "Failed to connect to automation server at %s, reconnecting in 5 seconds",
                    automationserver_url,
                )
                time.sleep(5)
    finally:
        if ping_thread is not None and ping_thread.is_alive():
            stop_ping_thread.set()
            ping_thread.join()
        logger.info("Worker stopped")

