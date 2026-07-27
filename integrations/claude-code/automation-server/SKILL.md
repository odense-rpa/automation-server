---
name: automation-server
description: >-
  Administer an Automation Server instance over its REST API — list/create/update processes,
  trigger runs, manage workqueues and workitems, inspect sessions, resolve incidents, and read
  audit logs. Use when the user wants to operate or inspect their Automation Server / RPA
  orchestrator (e.g. "trigger process X", "what's failing in the queue", "show open incidents",
  "add a workitem"). Requires a base URL and bearer token (ATS_BASE_URL / ATS_TOKEN env vars).
  Never touches credentials or access-token endpoints — those are out of scope by design.
---

# Automation Server admin

A thin, generic HTTP client (`scripts/ats`) for the Automation Server REST API. It handles auth,
URL building, and safety guards so you can drive the API by method + path instead of hand-rolling
`curl` calls.

## Setup

The user must provide a base URL and a bearer token. Ask for them if not already in the
environment:

```bash
export ATS_BASE_URL=http://localhost/api   # includes the /api prefix
export ATS_TOKEN=<their bearer token>
```

Then call the wrapper directly (it's executable):

```bash
~/.claude/skills/automation-server/scripts/ats GET /processes
```

If env vars aren't set, `--url` / `--token` flags also work. Never write the token to a file in
the repo or echo it back in full to the user.

## Golden rules

1. **Credentials and tokens are off-limits.** `ats` hard-blocks `/credentials*`, `/accesstokens*`,
   and `/token*` — don't try to work around this; the user does not want this skill touching
   secrets or minting auth material. If the user asks for credential management, tell them this
   skill intentionally doesn't support it.
2. **Confirm before destructive calls.** `DELETE` and workqueue `/clear` require `--confirm` and
   are refused otherwise. Before adding `--confirm`, make sure the user actually asked for the
   deletion/clear — don't infer it.
3. **Base URL already includes `/api`.** Don't prepend anything else — resource paths are e.g.
   `/processes`, not `/api/processes` or `/api/v1/processes`.
4. For the full endpoint/schema reference (request bodies, enums, pagination), read
   `references/endpoints.md` — don't guess field names.

## Quick catalog

| Resource | Base path | Notes |
|---|---|---|
| Processes | `/processes` | CRUD + `/​{id}/trigger` to attach a schedule/queue trigger |
| Triggers | `/triggers` | list/update/delete; `/upcoming` for next scheduled runs |
| Sessions | `/sessions` | a session = one run of a process; `POST /sessions` starts one now |
| Resources | `/resources` | worker machines; ping/heartbeat |
| Workqueues | `/workqueues` | CRUD, `/information` for status counts, `/​{id}/add`, `/​{id}/items`, `/​{id}/clear` |
| Workitems | `/workitems` | individual queue items; status transitions |
| Incidents | `/incidents` | failures needing triage; `/open`, `/​{id}/resolve` |
| Audit logs | `/audit-logs` | per-session or per-workitem log entries |
| Health | `/health`, `/health/ready` | no auth required |

## Recipes

**Trigger a process to run right now** (ad hoc, not scheduled):
```bash
ats POST /sessions --data '{"process_id": 5}'
```

**Give a process a recurring/scheduled trigger:**
```bash
ats POST /processes/5/trigger --data '{"type":"cron","cron":"0 */2 * * *","enabled":true}'
```

**Check a workqueue's backlog and drill into failures:**
```bash
ats GET /workqueues/information
ats GET /workqueues/3/items --query search=failed
```

**Add a work item to a queue:**
```bash
ats POST /workqueues/3/add --data '{"data":{"invoice_id":"INV-1"},"reference":"INV-1"}'
```

**Triage open incidents:**
```bash
ats GET /incidents/open
ats PUT /incidents/12/resolve --data '{"status":"dismissed","resolution_note":"transient network error"}'
```

**Recent activity across processes:**
```bash
ats GET /sessions/activity-summary --query hours=24
```

**Read logs for a run:**
```bash
ats GET /audit-logs/42
```

**Delete something (needs explicit user confirmation first):**
```bash
ats DELETE /workqueues/9 --confirm
```

For anything not covered here — exact request/response shapes, enum values, pagination params —
see `references/endpoints.md`.
