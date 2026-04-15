---
title: Production Deployment
sidebar_position: 2
description: Deploy Automation Server in a production environment.
---

For production, use the base `docker-compose.yml` directly, without the development override:

```bash
docker compose -f docker-compose.yml up -d
```

This uses the published images from GHCR rather than building locally.

## Environment

Before starting, make sure your `.env` file has production-appropriate values:

- Set a strong `ATS_TOKEN` — workers use this to authenticate with the backend
- Set strong `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` values
- Set `TZ` to your local timezone

See [Environment Variables](./environment-variables.md) for the full reference.

## Reverse Proxy

If you're running behind a reverse proxy (nginx, Traefik, Caddy), you don't need to expose port 80 directly. Comment out or remove `HTTP_PORT` from your `.env` and configure your proxy to forward to the frontend container.

{/* TODO: Add an example nginx reverse proxy configuration */}

## Scaling Workers

You can run multiple workers to process more automations in parallel. Workers can run on separate machines — set `ATS_URL` to point at your backend's external address, and `ATS_TOKEN` to match the backend's configured token.

```bash
ATS_URL=https://your-server/api
ATS_TOKEN=your-secret-token
ATS_CAPABILITIES=playwright
```

Each worker registers itself with the backend on startup and is assigned sessions based on its declared capabilities.
