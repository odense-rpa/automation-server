---
title: Quick Start
sidebar_position: 2
description: Get your first automation running in minutes.
---

After [installing](./installation.md) Automation Server, follow these steps to run your first automation.

## 1. Add a Resource

A "resource" is a worker that Automation Server can dispatch jobs to. Workers register themselves automatically when they start, but you can also add them manually through the web interface.

Navigate to **Resources** in the sidebar and confirm your worker appears there.

## 2. Create a Process

A "process" is a Python automation registered in the system. Navigate to **Processes** and create a new one. You'll need to point it at a Git repository containing your automation code.

Use the [process-template](https://github.com/odense-rpa/process-template) as a starting point, or the [test-process](https://github.com/odense-rpa/test-process) to try something immediately.

## 3. Add a Trigger

Once you have a process, attach a trigger to it. Navigate to the process detail page and add a trigger:

- **Cron** — runs on a schedule (e.g. `0 8 * * 1-5` for weekdays at 8am)
- **Date** — runs once at a specific date and time
- **Workqueue** — runs whenever items are waiting in a workqueue

## 4. Monitor Execution

When the trigger fires, Automation Server creates a session and dispatches it to an available worker. You can follow progress in the **Sessions** view, and inspect logs in the session detail page.

## Next Steps

- [Writing Automations](../guides/writing-automations.md) — learn how to build your own automation
- [Scheduling](../guides/scheduling.md) — understand trigger types in depth
- [Workqueues](../guides/workqueues.md) — distribute work across multiple sessions
