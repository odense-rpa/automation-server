---
title: Configuration
sidebar_position: 3
description: Environment variables and configuration options for Automation Server.
---

Automation Server is configured through environment variables in the `.env` file at the repository root. Copy `.env.example` to get started:

```bash
cp .env.example .env
```

## Timezone

```
TZ=Europe/Copenhagen
```

Sets the timezone used across all services. Use any [IANA timezone name](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

## Database

```
POSTGRES_USER=automation
POSTGRES_PASSWORD=automation
POSTGRES_DB=automation
```

Credentials for the PostgreSQL database. In development, the defaults from `.env.example` are fine. In production, use strong, unique values.

## Credential Encryption

```
ENCRYPTION_KEY=
```

Encrypts the username and password of stored credentials at rest in the database. Any non-empty string works as the key; use a long random value:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

The setting is optional:

- **Unset** — credentials are stored as plaintext. The server logs a warning on every startup, and the Credentials page shows a banner explaining that no key is configured.
- **Set** — credentials are encrypted whenever they are created or saved. Credentials that existed before the key was set remain plaintext until they are written again.

The API always returns decrypted values to authenticated clients, so workers and automations are unaffected by this setting.

Note that only the username and password are encrypted. The free-form **Data** field of a credential is stored as-is — do not put secrets there.

### Encrypting existing credentials

After setting a key on a server that already holds credentials, rewrite the existing rows in one pass:

- **Web interface** — the Credentials page shows how many credentials are still plaintext, with an **Encrypt all now** button.
- **API** — `POST /credentials/reencrypt`, which returns the number rewritten and the number remaining. It answers `409` if no key is configured.

Both cover soft-deleted credentials too, since their secrets are still on disk. Re-encryption does not change the credential values or their `updated_at` timestamp. Until it is run, the server logs a warning at startup naming how many credentials are still plaintext.

### If the key is lost or changed

There is no key rotation: a credential can only be read with the key it was saved under. If the server is started with a different `ENCRYPTION_KEY`, or with none at all, credentials encrypted under the previous key cannot be decrypted.

The server does not fail silently or return corrupt values in this case:

- Startup logs an error naming how many credentials are unreadable.
- The Credentials page shows a red banner explaining whether the key is missing or mismatched, and what to do about it.
- Credential API requests answer `500` with the same explanation, so workers fail loudly rather than running with empty passwords.

The fix is to restore the previous `ENCRYPTION_KEY` value and restart. If it is genuinely gone, the affected credentials must be deleted and re-entered.

:::warning
Back up the encryption key somewhere other than the server it runs on. Losing it means re-entering every credential by hand.
:::

## CORS

```
CORS_ALLOW_ORIGINS=
```

Origins the API accepts cross-origin browser requests from, as a comma-separated
list. Leave unset for same-origin only — correct for this compose setup, since the
frontend and API share the nginx proxy in front of them and the browser never makes
a cross-origin request. Only needed if you serve the frontend from a different
origin, such as a separately hosted SPA. Set to `*` to allow any origin.

## Workers

```
ATS_TOKEN=
ATS_URL=http://backend:8000
ATS_CAPABILITIES=
```

- **`ATS_TOKEN`** — authentication token workers use to connect to the backend. Leave empty for development. Set a strong secret in production.
- **`ATS_URL`** — the URL workers use to reach the backend API. The default `http://backend:8000` works within Docker Compose. Change this if your worker runs on a separate machine.
- **`ATS_CAPABILITIES`** — comma-separated list of capabilities the worker advertises. Processes are matched to workers based on these. For example, `playwright` means the worker can run browser automations. Leave this blank if you haven't customized your workers — processes without a required capability will run on any available worker.

## Deployment

```
# HTTP_PORT=80
```

Uncomment `HTTP_PORT` to change the port the frontend is exposed on. Useful when running behind a reverse proxy on a non-standard port.

See [Installation](./installation.md) for how these variables are used when starting the stack.
