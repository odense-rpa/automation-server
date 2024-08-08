import pydantic_settings
import logging
import socket
import time
import platform

from automationclient import resources, sessions
from runners import python


class Settings(pydantic_settings.BaseSettings):
    url: str = "http://localhost:8000/api"


settings = Settings()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

capabilities = f"python {platform.system()}".lower()

if __name__ == "__main__":
    logger.info("Starting worker")

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
                            "automationserver_url": settings.url,
                            "session_id": f"{session['id']}",
                            "resource_id": f"{resource['id']}",
                            "process_id": f"{process['id']}",
                        },
                    )
                    continue

                resources.ping_resource(resource["id"])
