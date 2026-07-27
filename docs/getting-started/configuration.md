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

- **Unset** — credentials are stored as plaintext. The web interface marks them with an "unencrypted" badge.
- **Set** — credentials are encrypted whenever they are created or saved. Credentials that existed before the key was set remain plaintext until they are saved again; open and save each one to encrypt it.

The API always returns decrypted values to authenticated clients, so workers and automations are unaffected by this setting.

:::warning
Back up the encryption key. If it is lost or changed, encrypted credentials cannot be recovered and must be re-entered manually.
:::

## Workers

```
ATS_TOKEN=
ATS_URL=http://backend:8000
ATS_CAPABILITIES=playwright
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
