---
title: Docker Setup
sidebar_position: 1
description: Running Automation Server with Docker Compose for development.
---

Docker Compose is the standard way to run Automation Server. The repository includes two compose files:

- `docker-compose.yml` — production base, uses published GHCR images
- `docker-compose.override.yml` — development overrides, applied automatically by `docker compose up`

## Development

For local development, run:

```bash
docker compose up --build
```

Docker Compose automatically merges `docker-compose.override.yml` on top of the base file. This gives you hot-reloading and local image builds.

To include the optional Adminer database admin tool:

```bash
docker compose --profile tools up
```

Adminer is available at `http://localhost:8080`.

## Services

| Service | Description |
|---|---|
| `backend` | FastAPI application, serves the REST API |
| `frontend` | Vue.js app served by nginx |
| `db` | PostgreSQL database |
| `worker` | Python worker that executes automations |

## Stopping Services

```bash
docker compose down
```

Add `-v` to also remove the database volume:

```bash
docker compose down -v
```

:::warning
`docker compose down -v` deletes all stored data including the database. Don't use this in production.
:::

See [Production Deployment](./production.md) for how to run in a production environment.
