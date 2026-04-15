---
title: Environment Variables
sidebar_position: 3
description: Complete reference of all environment variables for Automation Server.
---

All configuration is done through environment variables in the `.env` file at the repository root. Start from the provided example:

```bash
cp .env.example .env
```

## Reference

### `TZ`

**Default:** `Europe/Copenhagen`

The timezone used across all services. Affects scheduled trigger times and log timestamps. Use any [IANA timezone name](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

### `POSTGRES_USER`

**Default:** `automation`

The PostgreSQL database username. Used by both the database container and the backend.

### `POSTGRES_PASSWORD`

**Default:** `automation`

The PostgreSQL database password. Use a strong, unique value in production.

### `POSTGRES_DB`

**Default:** `automation`

The name of the PostgreSQL database.

### `ATS_TOKEN`

**Default:** *(empty)*

Authentication token that workers use to connect to the backend. Leave empty for local development. Set a strong secret in production — workers won't connect without a matching token.

### `ATS_URL`

**Default:** `http://backend:8000`

The URL workers use to reach the backend API. The default works within Docker Compose using the internal service name. Change this when running workers on separate machines.

### `ATS_CAPABILITIES`

**Default:** `playwright`

Comma-separated list of capabilities the worker advertises to the backend. Processes specify which capabilities they require, and Automation Server routes sessions to matching workers.

### `HTTP_PORT`

**Default:** *(not set)*

The host port to expose the frontend on. Uncomment and set this when you need a non-default port. Leave it unset when running behind a reverse proxy.
