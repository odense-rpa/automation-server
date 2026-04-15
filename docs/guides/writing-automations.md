---
title: Writing Automations
sidebar_position: 1
description: How to write Python automations for Automation Server.
---

An automation is a Python project that follows a specific structure so Automation Server can discover, deploy, and execute it on a worker.

## Getting Started

Use the [process-template](https://github.com/odense-rpa/process-template) to scaffold a new automation. It includes the boilerplate and framework integration you need.

```bash
git clone https://github.com/odense-rpa/process-template.git my-automation
cd my-automation
```

You can also explore the [test-process](https://github.com/odense-rpa/test-process) to see a working example.

## Project Structure

{/* TODO: Document the expected file structure, entry points, and how the worker discovers and runs the automation */}

## Framework API

{/* TODO: Document the Python framework for interacting with the server — logging, workqueue access, status reporting, and parameter handling */}

## Logging

Automation Server integrates with Python's standard `logging` module. Any log output from your automation is captured and stored against the session, making it easy to inspect what happened during execution.

See [Logging & Audit](./logging-and-audit.md) for more details.
