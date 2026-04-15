---
title: Logging & Audit
sidebar_position: 4
description: Built-in logging and audit trail for automation sessions.
---

Every session in Automation Server has a full audit trail. Log entries are grouped by session so you can see exactly what happened during each execution.

## How Logging Works

Automation Server integrates with Python's standard `logging` module. When your automation runs on a worker, log output is captured and stored against the session automatically — you don't need to set up file handlers or external log aggregation.

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Starting processing")
logger.warning("Item skipped: missing field")
logger.error("Failed to connect", exc_info=True)
```

All of these entries appear in the session log in the web interface.

## Viewing Logs

Navigate to **Sessions** in the web interface and open a session to see its log entries. Each entry shows the message, log level, timestamp, and — for errors — the full exception traceback.

## Incidents

When a session ends with a `FAILED` status and no incident exists yet, Automation Server automatically creates an incident. Incidents are only created for sessions that failed within the last 14 days, so legacy failures don't generate noise.

{/* TODO: Document incident statuses, resolution flow, and how to reschedule from an incident */}
