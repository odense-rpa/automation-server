import logging
import socket
import time
import platform
from requests.exceptions import ConnectionError

from automationclient import resources, sessions, automationserver_url, automationserver_token
from runners import python



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

capabilities = f"python {platform.system()}".lower()

if __name__ == "__main__":
    logger.info("Starting worker")
    while True:
        try:
            with resources.acquire_resource(
                fqdn=socket.getfqdn(),
                name=socket.gethostname(),
                capabilities=capabilities,
            ) as resource:
                while True:
                    with sessions.acquire_session(resource_id=resource["id"]) as session:
                        if session is None:
                            logger.info("No session")
                            time.sleep(10)
                            resources.ping_resource(resource["id"])
                            continue

                        process = sessions.get_process(session)

                        if process is None:
                            logger.error(f"Process not found for session {session}")
                            sessions.add_log_message(
                                session_id=session["id"], message="Process not found"
                            )
                            continue

                        logger.info(
                            f"Running {process['name']} (type: {process['target_type']})"
                        )

                        if process["target_type"] == "python":
                            python.run_python(
                                process["target_source"],
                                None,
                                environment={
                                    "ATS_URL": automationserver_url,
                                    "ATS_TOKEN": automationserver_token,
                                    "ATS_SESSION": f"{session['id']}",
                                    "ATS_RESOURCE": f"{resource['id']}",
                                    "ATS_PROCESS": f"{process['id']}",
                                },
                            )
                            continue

                        resources.ping_resource(resource["id"])
        except ConnectionError:
            logger.error(f"Failed to connect to automation server: {automationserver_url}, with token: {automationserver_token}, reconnecting in 5 seconds")
            time.sleep(5)
        
