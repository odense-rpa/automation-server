---
title: API Overview
sidebar_position: 1
description: REST API reference for Automation Server.
---

Automation Server exposes a REST API built with FastAPI. When the server is running, interactive API documentation is available at:

```
http://localhost/api/docs
```

This is powered by FastAPI's built-in Swagger UI, which lets you explore and test all endpoints directly in the browser.

## Authentication

{/* TODO: Document authentication — token-based auth for workers, and any auth for the web API */}

## Key Resources

| Resource | Base path | Description |
|---|---|---|
| Processes | `/processes` | Automation definitions |
| Sessions | `/sessions` | Execution instances |
| Triggers | `/triggers` | Schedules and conditions |
| Resources | `/resources` | Registered workers |
| Workqueues | `/workqueues` | Work item queues |
| Workitems | `/workqueues/{id}/items` | Items within a queue |
| Incidents | `/incidents` | Failed session incidents |
| Audit logs | `/auditlogs` | Session log entries |

{/* TODO: Document common request/response patterns, pagination, and error formats */}
