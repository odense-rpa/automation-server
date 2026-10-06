---
title: Workers
sidebar_position: 4
description: How workers connect to the backend and execute automations.
---

A "worker" is a Python process that connects to the backend, advertises its capabilities, and executes automation jobs assigned to it.

## Capabilities

Every worker advertises `python`, `playwright` and its OS name (for example `linux`) out of the box. Use the `ATS_CAPABILITIES` environment variable to add your own, for example on a worker that has SAP GUI installed:

```
ATS_CAPABILITIES=sap
```

Separate multiple capabilities with commas or spaces. Capabilities are lowercased, so use lowercase names in process requirements too.

When a process requires a specific capability (for example, `sap`), Automation Server only dispatches that process to workers that have declared that capability. A process with no requirements runs on any available worker.

You can run multiple workers with different capabilities on the same machine or across different machines.

## Execution

When a session is dispatched to a worker, the worker:

1. Clones the process's Git repository (including submodules)
2. Creates an isolated Python environment and installs dependencies
3. Runs the automation entry point
4. Streams log output back to the backend
5. Reports the final session status (`completed` or `failed`)

Each worker handles one session at a time. Run multiple workers to process multiple sessions in parallel.

## Running on a Separate Machine

Workers don't have to run on the same machine as the backend. Set these variables to connect to a remote backend:

```bash
ATS_URL=https://your-automation-server/api
ATS_TOKEN=your-secret-token
ATS_CAPABILITIES=sap
```

See [Configuration](../getting-started/configuration.md) for details.
