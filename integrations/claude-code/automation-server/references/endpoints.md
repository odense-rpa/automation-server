# Automation Server — endpoint reference

Base URL: user-supplied `ATS_BASE_URL` (e.g. `http://localhost/api`), already includes any proxy
prefix. All paths below are relative to it. Auth: `Authorization: Bearer <token>` (injected
automatically by `scripts/ats`).

**Excluded on purpose — do not call:** `/credentials*`, `/accesstokens*`, `/token*`. The `ats`
wrapper refuses these regardless of arguments.

## Shared shapes

`PaginatedResponse<T>`: `{ page, size, total_items, total_pages, items: [T] }`
Pagination query params (where supported): `page` (≥1, default 1), `size` (1–200, default 50),
`search` (optional free-text filter).

Enums:
- `TargetTypeEnum`: `python | blue_prism | ui_path | power_automate_desktop`
- `TriggerType`: `cron | workqueue | date`
- `WorkItemStatus`: `new | in progress | completed | failed | pending user action`
- `SessionStatus`: `new | in progress | completed | failed`
- `IncidentStatus`: `new | dismissed | rescheduled`

Common error codes: `404` not found, `410` gone (soft-deleted), `400` invalid state transition,
`204` no content (some GETs return this when nothing matches, e.g. `next_item`).

---

## Processes — `/processes`

| Method | Path | Description | Query / Body |
|---|---|---|---|
| GET | `/processes` | List processes | `?include_deleted=false` |
| GET | `/processes/{id}` | Get one | — |
| POST | `/processes` | Create | body `ProcessCreate` |
| PUT | `/processes/{id}` | Update | body `ProcessUpdate` |
| DELETE | `/processes/{id}` | Soft-delete | — (destructive, needs `--confirm`) |
| POST | `/processes/{id}/trigger` | Add a trigger to this process | body `TriggerCreate` |
| GET | `/processes/{id}/trigger` | List this process's triggers | `?include_deleted=false` |

`ProcessCreate` / `ProcessUpdate`:
```json
{
  "name": "string (required)",
  "description": "",
  "requirements": "",
  "target_type": "python|blue_prism|ui_path|power_automate_desktop (required)",
  "target_source": "",
  "target_credentials_id": null,
  "credentials_id": null,
  "workqueue_id": null
}
```
`target_credentials_id` / `credentials_id` are FKs into `/credentials` — pass the numeric id
through if the user already knows it; do not fetch or display the credential itself.

`Process` (response) adds: `id, deleted, created_at, updated_at`.

---

## Triggers — `/triggers` (creation via `POST /processes/{id}/trigger`)

| Method | Path | Description | Query / Body |
|---|---|---|---|
| GET | `/triggers` | List all | `?include_deleted=false` |
| GET | `/triggers/upcoming` | Next scheduled executions | `?hours_ahead=24` (1–168) |
| PUT | `/triggers/{id}` | Update | body `TriggerUpdate` |
| DELETE | `/triggers/{id}` | Soft-delete | — (destructive) |

`TriggerCreate` / `TriggerUpdate`:
```json
{
  "type": "cron|workqueue|date (required)",
  "cron": "",            "// required + valid cron expr when type=cron",
  "date": null,          "// ISO datetime, required when type=date",
  "workqueue_id": null,  "// required when type=workqueue",
  "workqueue_resource_limit": 0,
  "workqueue_scale_up_threshold": 0,
  "parameters": "",
  "enabled": false
}
```

`UpcomingExecutionRead`: `trigger_id, process_id, process_name, process_description,
next_execution, trigger_type, parameters, cron, date`.

---

## Sessions — `/sessions`

A session is one run/dispatch of a process on a resource.

| Method | Path | Description | Query / Body |
|---|---|---|---|
| GET | `/sessions` | Search/paginate | `?include_deleted=false&page=1&size=50&search=` |
| GET | `/sessions/new` | Undispatched sessions | — |
| GET | `/sessions/activity-summary` | Per-process counts | `?hours=24` |
| GET | `/sessions/{id}` | Get one | — |
| POST | `/sessions` | Start a session (run a process) | body `SessionCreate` |
| PUT | `/sessions/{id}/status` | Change status | body `SessionStatusUpdate` |
| GET | `/sessions/by_resource_id/{resource_id}` | Active session on a resource | 204 if none |

`SessionCreate`: `{ "process_id": <int, required>, "parameters": null }`
`SessionStatusUpdate`: `{ "status": "new|in progress|completed|failed" }`
Valid transitions: `new → in progress`; `in progress → completed|failed`. `failed` creates an
Incident; terminal states free the resource.

`Session` (response): `id, process_id, process, parameters, resource_id, resource, dispatched_at,
status, stop_requested, deleted, created_at, updated_at`.

---

## Resources — `/resources`

Worker machines that execute sessions.

| Method | Path | Description | Query / Body |
|---|---|---|---|
| GET | `/resources` | List (refreshes availability) | `?include_deleted=false` |
| GET | `/resources/{id}` | Get one | — |
| POST | `/resources` | Enroll | body `ResourceCreate` |
| PUT | `/resources/{id}` | Update (fqdn immutable) | body `ResourceUpdate` |
| PUT | `/resources/{id}/ping` | Heartbeat | — → `bool` |

`ResourceCreate` / `ResourceUpdate`: `{ "name": "...", "fqdn": "...", "capabilities": "..." }` (all required)

`Resource` (response): `id, name, fqdn, capabilities, available, last_seen, deleted, created_at, updated_at`.

---

## Workqueues — `/workqueues`

| Method | Path | Description | Query / Body |
|---|---|---|---|
| GET | `/workqueues` | List (sorted by name) | `?include_deleted=false` |
| GET | `/workqueues/information` | List + status counts | `?include_deleted=false` |
| GET | `/workqueues/{id}` | Get one | — |
| GET | `/workqueues/by_name/{name}` | Get by name | — |
| POST | `/workqueues` | Create | body `WorkqueueCreate` (422 if name exists) |
| PUT | `/workqueues/{id}` | Update | body `WorkqueueUpdate` |
| DELETE | `/workqueues/{id}` | Soft-delete | — (destructive) |
| POST | `/workqueues/{id}/clear` | Bulk-clear items | body `WorkqueueClear` (destructive) |
| POST | `/workqueues/{id}/add` | Add a work item | body `WorkItemCreate` |
| GET | `/workqueues/{id}/next_item` | Dequeue next NEW item | 204 if none/disabled |
| GET | `/workqueues/{id}/items` | Search/paginate items | `?page=1&size=50&search=` |
| GET | `/workqueues/{id}/by_reference/{reference}` | Items by reference in this queue | `?status=` |

`WorkqueueCreate` / `WorkqueueUpdate`: `{ "name": "...", "description": "...", "enabled": true }`
`WorkqueueClear`: `{ "workitem_status": null, "days_older_than": null }`
`WorkItemCreate`: `{ "data": {}, "reference": "" }`
`WorkqueueInformation` (response): `id, name, description, enabled, new, in_progress, completed,
failed, pending_user_action`.

---

## Workitems — `/workitems` (creation via `POST /workqueues/{id}/add`)

| Method | Path | Description | Query / Body |
|---|---|---|---|
| GET | `/workitems/{id}` | Get one | — |
| PUT | `/workitems/{id}` | Update data/reference | body `WorkItemUpdate` |
| PUT | `/workitems/{id}/status` | Change status | body `WorkItemStatusUpdate` |
| GET | `/workitems/by-reference/{reference}` | Items by reference (all queues) | `?status=` |

`WorkItemUpdate`: `{ "data": {...}, "reference": "..." }` (both optional)
`WorkItemStatusUpdate`: `{ "status": "new|in progress|completed|failed|pending user action" (required), "message": null }`

`WorkItem` / `WorkItemRead` (response): `id, data, reference, locked, status, message,
workqueue_id, started_at, work_duration_seconds, created_at, updated_at`.

---

## Incidents — `/incidents`

A failed session creates an incident automatically.

| Method | Path | Description | Query / Body |
|---|---|---|---|
| GET | `/incidents` | Search/paginate | `?status=&page=1&size=50&search=` |
| GET | `/incidents/open` | List open | — |
| GET | `/incidents/open/count` | Count open | → `{ "count": int }` |
| POST | `/incidents/dismiss-all` | Dismiss all open | → `{ "dismissed": int }` |
| GET | `/incidents/{id}` | Get one | — |
| PUT | `/incidents/{id}/resolve` | Resolve | body `IncidentResolve` |
| DELETE | `/incidents/{id}` | Delete | — (destructive) |

`IncidentResolve`: `{ "status": "dismissed|rescheduled" (required), "resolution_note": null }`
Valid transitions: `new → dismissed|rescheduled` only.

`Incident` (response): `id, session_id, session, process_id, status, error_trace, resolution_note,
ai_resolution_suggestion, rescheduled_session_id, deleted, created_at, updated_at`.

---

## Audit logs — `/audit-logs`

| Method | Path | Description | Query / Body |
|---|---|---|---|
| POST | `/audit-logs` | Create a log entry | body `AuditLogCreate` |
| GET | `/audit-logs/{session_id}` | Paginated logs for a session | `?page=1&size=50&search=` |
| GET | `/audit-logs/by_workitem/{item_id}` | Logs for a work item | — |

`AuditLogCreate`: `{ session_id, workitem_id, "message" (required), "level": "INFO",
"logger_name": "", module, function_name, line_number, exception_type, exception_message,
traceback, structured_data: {}, "event_timestamp" (required, ISO datetime) }`

`AuditLog` (response): `id, session_id, session, workitem_id, workitem, message, level,
logger_name, module, function_name, line_number, exception_type, exception_message, traceback,
structured_data, event_timestamp, created_at`.

---

## Health — no auth required

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness → `{status, timestamp, version}` |
| GET | `/health/ready` | Readiness incl. DB → `{status, timestamp, version, database}` |

---

## Excluded — do not call

- `/credentials*` — stores/returns plaintext username/password/secret data.
- `/accesstokens*` — mints/lists/deletes bearer tokens (auth material).
- `/token*` — OAuth2 login/token-exchange endpoint.

These are blocked at the `ats` wrapper level. If a task seems to require them (e.g. "look up the
credential for X"), tell the user this skill deliberately doesn't support credential/token
management and point them to the Automation Server UI instead.
