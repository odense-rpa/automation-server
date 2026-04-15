---
title: Setup a Process
sidebar_position: 1
description: Create a workqueue, a process, and a trigger to start processing items automatically.
---

This guide walks you through setting up an end-to-end automation: a workqueue to hold your work items, a process to handle them, and a trigger to fire the automation when items are waiting.

## Create the Workqueue

Navigate to **Workqueues** in the sidebar and click **+ Create**. Give your workqueue a descriptive name — your automation will reference it by name, so choose something that reflects what the queue holds.

![Creating a workqueue](/img/guide-setup-create-workqueue.png)

Once created, the workqueue appears in the list. Items are added programmatically by your automations.

## Create the Process

Navigate to **Processes** in the sidebar and click **+ Create**. Fill in the details:

- **Name** — a human-readable label for the automation
- **Git repository** — the URL of the repository containing your automation code
- **Requirements** — leave as `python` unless your automation needs specific packages

![Creating a process](/img/guide-setup-create-process.png)

If you haven't written an automation yet, use our [process-template](https://github.com/odense-rpa/process-template) to get started, or just point it at our [test-process](https://github.com/odense-rpa/test-process.git) to see something run right away.

![Process created](/img/guide-setup-process-created.png)

## Create a Trigger

Open the process you just created and navigate to the **Triggers** tab. You can add multiple triggers to the same process.

### Cron trigger

To run the process on a fixed schedule, click **+ Add trigger** and select **Cron**. For a daily run at 8am, use:

```
0 8 * * *
```

You can pass parameters to the process at trigger time. A common convention is to pass `--queue` so the automation knows it should read from a workqueue — though this is just a convention, not a requirement enforced by Automation Server.

![Creating a cron trigger](/img/guide-setup-cron.png)

### Workqueue trigger

To run the process automatically whenever items are waiting, click **+ Add trigger** and select **Workqueue**. Choose the workqueue you created in the first step.

![Creating a workqueue trigger](/img/guide-setup-workqueue.png)

Automation Server will monitor the queue and dispatch a session to an available worker whenever items are waiting.

## Next Steps

With the workqueue, process, and trigger in place, you can start pushing items into the queue. See [Workqueues](./workqueues.md) for how to add items programmatically from your automations.
