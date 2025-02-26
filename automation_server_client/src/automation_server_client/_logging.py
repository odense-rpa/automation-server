import logging
import requests

from ._config import AutomationServerConfig

# Custom HTTP Handler for logging
class AutomationServerLoggingHandler(logging.Handler):
    def __init__(self):
        super().__init__()

    def emit(self, record):
        print("Sending log")
        log_entry = self.format(record)  # Format the log record
        log_data = { "workitem_id": 0, "message": log_entry }

        if AutomationServerConfig.session is None or AutomationServerConfig.url == "":
            return

        if AutomationServerConfig.workitem_id is not None:
            log_data["workitem_id"] = AutomationServerConfig.workitem_id

        try:
            response = requests.post(
                f"{AutomationServerConfig.url}/sessions/{AutomationServerConfig.session}/log",
                headers={"Authorization": f"Bearer {AutomationServerConfig.token}"},
                json=log_data,
            )
            response.raise_for_status()
        except Exception as e:
            # Handle any exceptions that occur when sending the log
            print(f"Failed to send log to {self.url}: {e}")
