import json
import logging
import requests

from dataclasses import dataclass
from datetime import datetime

from ._config import AutomationServerConfig

@dataclass
class Session:
    id: int
    process_id: int
    resource_id: int
    dispatched_at: str
    status: str
    stop_requested: bool
    deleted: bool
    parameters: str
    created_at: str
    updated_at: str

    def get_session(session_id):
        response = requests.get(
            f"{AutomationServerConfig.url}/sessions/{session_id}",
            headers={"Authorization": f"Bearer {AutomationServerConfig.token}"},
        )
        response.raise_for_status()

        return Session(**response.json())

@dataclass
class Process:
    id: int
    name: str
    description: str
    requirements: str
    target_type: str
    target_source: str
    target_credentials_id: int
    credentials_id: int
    workqueue_id: int
    deleted: bool
    created_at: str
    updated_at: str

    def get_process(process_id):
        response = requests.get(
            f"{AutomationServerConfig.url}/processes/{process_id}",
            headers={"Authorization": f"Bearer {AutomationServerConfig.token}"},
        )
        response.raise_for_status()

        return Process(**response.json())

@dataclass
class Workqueue:
    id: int
    name: str
    description: str
    enabled: bool
    deleted: bool
    created_at: str
    updated_at: str

    def add_item(self, data: dict, reference: str):
        response = requests.post(
            f"{AutomationServerConfig.url}/workqueues/{self.id}/add",
            headers={"Authorization": f"Bearer {AutomationServerConfig.token}"},
            json={"data": json.dumps(data), "reference": reference},
        )
        response.raise_for_status()

        return WorkItem(**response.json())

    def get_workqueue(workqueue_id):
        response = requests.get(
            f"{AutomationServerConfig.url}/workqueues/{workqueue_id}",
            headers={"Authorization": f"Bearer {AutomationServerConfig.token}"},
        )
        response.raise_for_status()

        return Workqueue(**response.json())

    def clear_workqueue(self, workitem_status=None, days_older_than=None):
        response = requests.post(
            f"{AutomationServerConfig.url}/workqueues/{self.id}/clear",
            json={
                "workitem_status": workitem_status,
                "days_older_than": days_older_than,
            },
            headers={"Authorization": f"Bearer {AutomationServerConfig.token}"},
        )
        response.raise_for_status()

    def __iter__(self):
        return self

    def __next__(self):
        response = requests.get(
            f"{AutomationServerConfig.url}/workqueues/{self.id}/next_item",
            headers={"Authorization": f"Bearer {AutomationServerConfig.token}"},
        )

        if response.status_code == 204:
            raise StopIteration

        response.raise_for_status()

        AutomationServerConfig.workitem_id = response.json()["id"]

        return WorkItem(**response.json())


@dataclass
class WorkItem:
    id: int
    data: str
    reference: str
    locked: bool
    status: str
    message: str
    workqueue_id: int
    created_at: str
    updated_at: str


    def get_data_as_dict(self) -> dict:
        return json.loads(self.data)

    def update(self, data: dict):
        response = requests.put(
            f"{AutomationServerConfig.url}/workitems/{self.id}",
            headers={"Authorization": f"Bearer {AutomationServerConfig.token}"},
            json={"data": json.dumps(data), "reference": self.reference},
        )
        response.raise_for_status()
        self.data = json.dumps(data)
       


    def __enter__(self):
        logger = logging.getLogger(__name__)
        logger.debug(f"Processing {self}")
        AutomationServerConfig.workitem_id = self.id

    def __exit__(self, exc_type, exc_value, traceback):
        logger = logging.getLogger(__name__)
        AutomationServerConfig.workitem_id = None
        if exc_type:
            logger.error(
                f"An error occurred while processing {self}: {exc_value}"
            )
            self.fail(str(exc_value))

        # If we are working on an item that is in progress, we will mark it as completed
        if self.status == "in progress":
            self.complete("Completed")

    def __str__(self) -> str:
        return f"WorkItem(id={self.id}, reference={self.reference}, data={self.data})"

    def fail(self, message):
        self.update_status("failed", message)

    def complete(self, message):
        self.update_status("completed", message)

    def pending_user(self, message):
        self.update_status("pending user action", message)

    def update_status(self, status, message: str = ""):
        response = requests.put(
            f"{AutomationServerConfig.url}/workitems/{self.id}/status",
            headers={"Authorization": f"Bearer {AutomationServerConfig.token}"},
            json={"status": status, "message": message},
        )
        response.raise_for_status()
        self.status = status
        self.message = message

@dataclass
class Credential:
    id: int
    name: str
    data: str
    username: str
    password: str
    deleted: bool
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def get_credential(credential: str) -> "Credential":
        
        response = requests.get(
            f"{AutomationServerConfig.url}/credentials/by_name/{requests.utils.quote(credential)}",
            headers={"Authorization": f"Bearer {AutomationServerConfig.token}"},
        )
        response.raise_for_status()

        return Credential(**response.json())

    def get_data_as_dict(self) -> dict:
        return json.loads(self.data)
