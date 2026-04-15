---
title: Installation
sidebar_position: 1
description: How to install and set up Automation Server using Docker.
slug: /
---

You need Docker and Docker Compose installed on your machine. That's the only requirement — everything else runs inside containers.

## Download the Configuration Files

Create a directory and download the three files you need:

```bash
mkdir automation-server && cd automation-server

curl -O https://raw.githubusercontent.com/odense-rpa/automation-server/main/docker-compose.yml
curl -O https://raw.githubusercontent.com/odense-rpa/automation-server/main/nginx.conf
curl -o .env https://raw.githubusercontent.com/odense-rpa/automation-server/main/.env.example
```

## Configure the Environment

Open `.env` and adjust the values for your setup. The defaults work for a quick local test, but you should set strong credentials before exposing the service to a network.

See [Configuration](./configuration.md) for details on each variable.

## Start Services

```bash
docker compose up -d
```

This starts the backend API, the frontend web interface, the database, and the worker.

## Verify Installation

Once the containers are running, open your browser and go to:

```
http://localhost
```

You should see the Automation Server web interface. The backend API documentation is available at:

```
http://localhost/api/docs
```

## Next Steps

Follow the [Quick Start](./quick-start.md) guide to run your first automation.
