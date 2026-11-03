---
title: Datastores
sidebar_position: 2
description: Keep state between runs in named JSON documents.
---

A datastore is a named JSON document that automations can read and write between runs. Use it for state that has to survive from one run to the next: where the last run stopped, counters, how recent cases were distributed between teams, and similar. It is too small to justify a database and too structured for a spreadsheet.

Each run of an automation starts in a fresh folder that is deleted afterwards, so anything not stored in Automation Server is lost when the run ends.

## What a datastore is

- **One JSON object** (`{...}`), read and written as a whole. Structure the object however you like.
- **Found by name or id.** Names are case-sensitive and unique among datastores that aren't deleted; a deleted name can be used again.
- **Not owned by a process.** Any automation can use any datastore, so several processes can share one. The Datastores page shows them all.
- **Versioned for safe updates.** Every write increases `version`, which lets concurrent runs detect each other (see [Concurrent runs](#concurrent-runs)). There is no history: only the current document is kept.

## What it is not

- **Not for secrets.** Documents are [encrypted at rest](../getting-started/configuration.md#encryption-at-rest) when the server has an encryption key, but the API returns them in full to anyone with access and the web interface shows them. Use [credentials](./writing-automations.md#credentials) for passwords, tokens and keys.
- **Not a database.** There are no queries: a datastore is read and written whole, by name or id.
- **Not file storage.** A document can be at most 1 MB of JSON (the `DATASTORE_MAX_BYTES` setting).

## In the web interface

**Datastores** in the menu lists every datastore with its size, version and when it last changed. Open one to see its document, edit it, or delete it.

Editing is safe against automations writing at the same time: if a datastore changed after you opened the editor, saving is refused with a "changed since you opened it" message instead of overwriting the automation's change. Reload to see the current document.

## From an automation

The API uses the same `ATS_URL` and `ATS_TOKEN` as the rest of the framework.

| Request | Purpose |
|---|---|
| `GET /datastores/by_name/{name}` | Read a datastore (`404` if it doesn't exist) |
| `PUT /datastores/by_name/{name}` | Write the document, **creating the datastore if it doesn't exist** (`201` created, `200` updated) |
| `GET /datastores/{id}`, `PUT /datastores/{id}` | The same by id |

A write sends the whole document as `data`:

```python
import os

import httpx

url = os.environ["ATS_URL"]
headers = {"Authorization": f"Bearer {os.environ['ATS_TOKEN']}"}

response = httpx.put(
    f"{url}/datastores/by_name/team-distribution",
    headers=headers,
    json={"data": {"last_run": "2026-11-03", "counts": {"A": 12, "B": 9}}},
)
response.raise_for_status()
```

Reading a datastore that doesn't exist yet returns `404`; treat that as "start from an empty document". Nothing is created by reading.

### Concurrent runs

If a process can run in more than one session at the same time (a workqueue trigger that scales up across several workers, for example), two runs can read the same document, change it, and write it back. Without care, one run silently overwrites the other's change.

To prevent that, send the `version` you read as `expected_version`. The write only succeeds if nobody else wrote in the meantime; otherwise it is refused with `409`, and you read again and retry:

```python
def update_datastore(name: str, change, attempts: int = 5) -> dict:
    """Read, change and write a datastore, retrying if another run wrote first."""
    for _ in range(attempts):
        response = httpx.get(f"{url}/datastores/by_name/{name}", headers=headers)
        if response.status_code == 404:
            data, version = {}, 0  # 0: create it, unless another run just did
        else:
            response.raise_for_status()
            body = response.json()
            data, version = body["data"], body["version"]

        response = httpx.put(
            f"{url}/datastores/by_name/{name}",
            headers=headers,
            json={"data": change(data), "expected_version": version},
        )
        if response.status_code != 409:
            response.raise_for_status()
            return response.json()["data"]

    raise RuntimeError(f"Datastore '{name}' kept changing; gave up after {attempts} attempts")
```

`expected_version: 0` means "the datastore must not exist yet", so two runs creating the same datastore at once can't both succeed. Leaving `expected_version` out writes regardless of what is there (last writer wins), which is fine when only one run at a time can write.
