"""
Locust benchmark scenarios for automation-server.

Two user classes reflecting real traffic shape:
  ReaderUser (weight 7) — scheduler + dashboard polling
  WriterUser (weight 3) — workitem enqueue + resource keep-alive

Run after seeding:
    uv run locust -f benchmarks/locustfile.py \\
        --host http://localhost:8000 \\
        --users 50 --spawn-rate 10 --run-time 2m \\
        --headless --csv results/<branch-name>
"""

import json
import random
from pathlib import Path

from locust import HttpUser, between, task

_ids_path = Path(__file__).parent / "seed-ids.json"
if not _ids_path.exists():
    raise FileNotFoundError(
        f"seed-ids.json not found at {_ids_path}. Run benchmarks/seed.py first."
    )

_ids = json.loads(_ids_path.read_text())
WORKQUEUE_ID: int = _ids["workqueue"]
RESOURCE_IDS: list[int] = _ids["resources"]
WORKITEM_IDS: list[int] = _ids["workitems"]

AUTH = {"Authorization": "Bearer development-token"}


class ReaderUser(HttpUser):
    """Simulates the scheduler loop and dashboard polling (read-heavy)."""

    weight = 7
    wait_time = between(0, 0.05)

    @task(5)
    def next_item(self) -> None:
        # 204 is normal when the queue is empty — not an error
        with self.client.get(
            f"/api/v1/workqueues/{WORKQUEUE_ID}/next_item",
            headers=AUTH,
            catch_response=True,
            name="/api/v1/workqueues/[id]/next_item",
        ) as r:
            if r.status_code in (200, 204):
                r.success()

    @task(3)
    def workqueue_information(self) -> None:
        self.client.get("/api/v1/workqueues/information", headers=AUTH)

    @task(2)
    def list_resources(self) -> None:
        self.client.get("/api/v1/resources", headers=AUTH)

    @task(2)
    def get_workitem(self) -> None:
        item_id = random.choice(WORKITEM_IDS)
        self.client.get(
            f"/api/v1/workitems/{item_id}",
            headers=AUTH,
            name="/api/v1/workitems/[id]",
        )

    @task(1)
    def list_workqueues(self) -> None:
        self.client.get("/api/v1/workqueues", headers=AUTH)


class WriterUser(HttpUser):
    """Simulates workers enqueuing items and resources pinging in."""

    weight = 3
    wait_time = between(0, 0.05)

    @task(5)
    def enqueue_item(self) -> None:
        self.client.post(
            f"/api/v1/workqueues/{WORKQUEUE_ID}/add",
            json={"data": {"bench": True}, "reference": ""},
            headers=AUTH,
            name="/api/v1/workqueues/[id]/add",
        )

    @task(3)
    def ping_resource(self) -> None:
        resource_id = random.choice(RESOURCE_IDS)
        self.client.put(
            f"/api/v1/resources/{resource_id}/ping",
            headers=AUTH,
            name="/api/v1/resources/[id]/ping",
        )
