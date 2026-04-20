#!/usr/bin/env python3
"""
Seed the database with a known, reproducible dataset for benchmarking.

Creates:
  1 workqueue | 10 processes | 100 resources | 1000 workitems

Writes benchmark/seed-ids.json so locustfile.py can load IDs without re-discovery.
Aborts early if the benchmark workqueue already exists to prevent double-seeding.

Usage:
    uv run python benchmarks/seed.py [--host http://localhost:8000]
"""

import argparse
import json
import sys
from pathlib import Path

import httpx

WORKQUEUE_NAME = "benchmark-queue"
N_PROCESSES = 10
N_RESOURCES = 100
N_WORKITEMS = 1000

HEADERS = {"Authorization": "Bearer development-token"}


def post(client: httpx.Client, path: str, body: dict) -> dict:
    r = client.post(path, json=body, headers=HEADERS)
    if not r.is_success:
        print(f"  ERROR {r.status_code} {path}: {r.text[:200]}", file=sys.stderr)
        sys.exit(1)
    return r.json()


def main(host: str) -> None:
    ids: dict = {"workqueue": None, "processes": [], "resources": [], "workitems": []}

    with httpx.Client(base_url=host, timeout=30) as client:
        # Idempotency guard
        r = client.get("/workqueues", headers=HEADERS)
        r.raise_for_status()
        existing = [q["name"] for q in r.json()]
        if WORKQUEUE_NAME in existing:
            print(
                f"Workqueue '{WORKQUEUE_NAME}' already exists — aborting to prevent double-seed.\n"
                "Run 'docker compose down -v && docker compose up -d' to reset the DB.",
                file=sys.stderr,
            )
            sys.exit(1)

        # 1. Workqueue
        print(f"Creating workqueue '{WORKQUEUE_NAME}' ...", end=" ", flush=True)
        q = post(client, "/workqueues", {"name": WORKQUEUE_NAME, "description": "Benchmark queue", "enabled": True})
        ids["workqueue"] = q["id"]
        print(f"id={q['id']}")

        # 2. Processes
        print(f"Creating {N_PROCESSES} processes ...", end=" ", flush=True)
        for i in range(N_PROCESSES):
            p = post(
                client,
                "/processes",
                {
                    "name": f"bench-process-{i:03d}",
                    "description": "benchmark",
                    "target_type": "python",
                    "workqueue_id": q["id"],
                },
            )
            ids["processes"].append(p["id"])
        print(f"ids {ids['processes'][0]}..{ids['processes'][-1]}")

        # 3. Resources
        print(f"Creating {N_RESOURCES} resources ...", end=" ", flush=True)
        for i in range(N_RESOURCES):
            res = post(
                client,
                "/resources",
                {
                    "name": f"bench-resource-{i:03d}",
                    "fqdn": f"bench-resource-{i:03d}.local",
                    "capabilities": "benchmark",
                },
            )
            ids["resources"].append(res["id"])
        print(f"ids {ids['resources'][0]}..{ids['resources'][-1]}")

        # 4. Workitems
        print(f"Creating {N_WORKITEMS} workitems ...", end=" ", flush=True)
        for i in range(N_WORKITEMS):
            item = post(
                client,
                f"/workqueues/{q['id']}/add",
                {"data": {"index": i}, "reference": f"bench-item-{i:04d}"},
            )
            ids["workitems"].append(item["id"])
        print(f"ids {ids['workitems'][0]}..{ids['workitems'][-1]}")

    out = Path(__file__).parent / "seed-ids.json"
    out.write_text(json.dumps(ids, indent=2))
    print(f"\nSeed complete. IDs written to {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="http://localhost:8000")
    args = parser.parse_args()
    main(args.host)
