---
title: Workqueues
sidebar_position: 3
description: Use workqueues to manage and distribute work items across automation sessions.
---

A "workqueue" is a named list of items your automation processes one by one. Instead of hardcoding work into your automation, you push items into a queue and let Automation Server dispatch sessions to process them.

This is useful when you have a variable amount of work arriving over time — for example, a list of cases to process, files to transform, or records to update.

## Creating a Workqueue

Navigate to **Workqueues** in the web interface and create a new queue. Give it a descriptive name — your automations will reference it by name.

## Adding Items

{/* TODO: Document how to add items via the API and via the Python framework from within an automation */}

## Processing Items

{/* TODO: Document how an automation claims and processes items from a queue, and how to mark them complete, failed, or pending user action */}

## Item Status

Each workqueue item has a status:

| Status | Meaning |
|---|---|
| `new` | Waiting to be processed |
| `in progress` | Currently being processed by a session |
| `completed` | Successfully processed |
| `failed` | Processing failed |
| `pending user action` | Waiting for a human to review or act |

## Workqueue Triggers

You can attach a workqueue trigger to a process so that Automation Server automatically creates sessions when items are waiting. See [Scheduling](./scheduling.md) for details.
