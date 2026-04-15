---
title: Writing Automations
sidebar_position: 1
description: How to write Python automations for Automation Server.
---

An automation is a Python project that follows a specific structure so Automation Server can discover, deploy, and execute it on a worker.

:::warning
Automation Server assumes your project uses [uv](https://github.com/astral-sh/uv) for package management. Other tools may not work correctly and are unsupported.
:::

## Getting Started

Use the [process-template](https://github.com/odense-rpa/process-template) to scaffold a new automation. It includes the boilerplate and framework integration you need.

```bash
git clone https://github.com/odense-rpa/process-template.git my-automation
cd my-automation
```

Remove the template's git history and start fresh with your own repository:

```bash
rm -rf .git
git init
```

You can also explore the [test-process](https://github.com/odense-rpa/test-process) to see a working example.

## The Template

The template's `main.py` has two entry points: one for populating the workqueue, and one for processing it.

```python
async def populate_queue(workqueue: Workqueue):
    # Add items to the workqueue here
    pass


async def process_workqueue(workqueue: Workqueue):
    for item in workqueue:
        with item:
            data = item.data  # Item data deserialized from JSON as dict

            try:
                # Process the item here
                pass
            except WorkItemError as e:
                # WorkItemError marks the item for manual review
                item.fail(str(e))
```

At the bottom, the `--queue` argument controls which path runs:

```python
if __name__ == "__main__":
    ats = AutomationServer.from_environment()
    workqueue = ats.workqueue()

    if "--queue" in sys.argv:
        workqueue.clear_workqueue(WorkItemStatus.NEW)
        asyncio.run(populate_queue(workqueue))
        exit(0)

    asyncio.run(process_workqueue(workqueue))
```

So a cron trigger with `--queue` clears and repopulates the queue on a schedule, while a workqueue trigger (without `--queue`) processes whatever items are waiting. You don't have to follow this pattern — it's just a convenient convention the template gives you.

Dependencies are declared in `pyproject.toml` and managed by [uv](https://github.com/astral-sh/uv). The worker installs them automatically before each run.

## Framework API

To interact with Automation Server from your automation, you need the [automation-server-client](https://github.com/odense-rpa/automation-server-client) package. It's already included in the process-template, but you can add it to any project with:

```bash
uv add "git+https://github.com/odense-rpa/automation-server-client.git"
```

### AutomationServer

The main entry point. Call `from_environment()` to initialize it from environment variables — the worker sets these automatically before running your automation.

```python
from automation_server_client import AutomationServer

ats = AutomationServer.from_environment()
```

### Workqueue

Access the workqueue associated with your process:

```python
workqueue = ats.workqueue()
```

Add items to the queue:

```python
workqueue.add_item(data={"case_id": 123}, reference="case-123")
```

Iterate over waiting items — each item is automatically marked in progress when entered and completed when the `with` block exits cleanly:

```python
for item in workqueue:
    with item:
        data = item.data  # dict, deserialized from JSON
        # process item...
```

### WorkItem status

Inside the `with` block you can explicitly set the item outcome:

```python
item.complete("Done")               # mark completed
item.fail("Something went wrong")   # mark failed
item.pending_user("Needs review")   # mark pending user action
```

Raising `WorkItemError` is a shorthand for a soft failure that routes the item to manual review.

### Credentials

Retrieve named credentials stored in Automation Server:

```python
from automation_server_client import Credential

cred = Credential.get_by_name(ats, "my-system")
print(cred.username, cred.password)
```

### Logging

Standard Python logging is captured automatically and stored against the session. No extra setup needed — just use `logging.getLogger(__name__)` as usual.

## Logging

Automation Server integrates with Python's standard `logging` module. Any log output from your automation is captured and stored against the session, making it easy to inspect what happened during execution.

See [Logging & Audit](./logging-and-audit.md) for more details.
