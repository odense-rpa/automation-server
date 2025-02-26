import logging

from ._config import AutomationServerConfig
from ._logging import AutomationServerLoggingHandler
from ._models import Session, Process, Workqueue


class AutomationServer:
    session_id = None

    def __init__(self, session_id=None):
        session_id = session_id
        self.workqueue_id = None

        self.url = AutomationServerConfig.url
        self.token = AutomationServerConfig.token

        if session_id is not None:
            self.session = Session.get_session(session_id)
            self.process = Process.get_process(self.session.process_id)
            if self.process.workqueue_id > 0:
                self.workqueue_id = self.process.workqueue_id
        else:
            self.session = None
            self.process = None

        if AutomationServerConfig.workqueue_override is not None:
            self.workqueue_id = AutomationServerConfig.workqueue_override

    def workqueue(self):
        if self.workqueue_id is None:
            raise ValueError("workqueue_id is not set")

        return Workqueue.get_workqueue(self.workqueue_id)

    def from_environment():
        AutomationServerConfig.init_from_environment()

        logging.basicConfig(
            level=logging.INFO,
            handlers=[AutomationServerLoggingHandler(), logging.StreamHandler()],
        )

        return AutomationServer(AutomationServerConfig.session)

    def __str__(self):
        return f"AutomationServer(url={self.url}, session = {self.session}, process = {self.process}, workqueue_id={self.workqueue_id})"


class WorkItemError(Exception):
    pass
