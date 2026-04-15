---
title: Overview
sidebar_position: 1
description: High-level architecture of Automation Server.
---

Automation Server consists of three main components that work together to manage and execute Python automations.

## Components

**Backend** — A Python [FastAPI](https://fastapi.tiangolo.com) application that manages processes, schedules, workqueues, sessions, and resources. It exposes a REST API consumed by both the frontend and the workers.

**Frontend** — A [Vue.js](https://vuejs.org) web interface served by nginx. It lets you monitor running automations, manage processes and triggers, inspect workqueue items, and view audit logs.

**Worker** — A Python process that connects to the backend, declares its capabilities, and executes assigned automation jobs. Each worker runs one automation at a time in an isolated environment to ensure package integrity and stability.

## How It Works

1. You define a **process** — a pointer to a Git repository containing your automation code, along with its required capabilities and parameters.
2. You attach a **trigger** to the process — a cron schedule, a specific date/time, or a workqueue condition.
3. When the trigger fires, the backend creates a **session** and looks for an available **resource** (worker) that matches the process's required capabilities.
4. The worker clones the process repository, installs its dependencies in an isolated environment, and runs the automation.
5. Log output is captured and stored against the session. When the session ends, its status is updated to `completed` or `failed`.

## Layered Architecture

The backend follows a layered architecture:

- **API layer** (`backend/app/api/`) — FastAPI routers handle HTTP requests and delegate to services
- **Service layer** (`backend/app/services/`) — business logic and orchestration
- **Repository layer** (`backend/app/database/repository/`) — data access using SQLModel ORM
- **Database** — PostgreSQL

{/* TODO: Add architecture diagram */}
