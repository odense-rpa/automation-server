---
title: Backend
sidebar_position: 2
description: Backend API architecture and internal structure.
---

The backend is a [FastAPI](https://fastapi.tiangolo.com) application written in Python. It handles all business logic, database access, and scheduling.

## Structure

```
backend/app/
├── api/v1/          # FastAPI routers (one per resource)
├── services/        # Business logic
├── database/
│   ├── models.py    # SQLModel ORM models
│   └── repository/  # Data access layer
├── scheduler/       # Modular scheduler
└── config.py        # Configuration
```

## Scheduler

The scheduler runs as a background task and periodically checks for triggers to fire. It uses the Strategy pattern — each trigger type (cron, date, workqueue) is handled by a dedicated processor.

See `backend/app/scheduler/` for the implementation. Adding a new trigger type means creating a new processor class and registering it in the registry.

{/* TODO: Document the scheduler loop, resource allocation, and session dispatching in more detail */}

## Database

The database is PostgreSQL. Schema migrations are managed by Alembic.

```bash
cd backend
uv run alembic upgrade head
```

Models are defined in `backend/app/database/models.py` using SQLModel, which combines SQLAlchemy and Pydantic.

### Encryption at rest

When `ENCRYPTION_KEY` is set, credential usernames and passwords and datastore documents are encrypted at rest using Fernet (AES-128-CBC with HMAC). The implementation lives in `backend/app/database/crypto.py` as SQLAlchemy type decorators (`EncryptedStr` for credentials, `EncryptedJSON` for datastores, which stores the JSON as text), so encryption and decryption happen transparently at the column level — services, repositories, and the API work with plaintext values. Encrypted values carry an `enc:v1:` prefix in the database; values without the prefix are treated as legacy plaintext and pass through unchanged.

Because the prefix distinguishes the two, repositories can find legacy rows with raw SQL that bypasses the type decorators. `EncryptedColumnsMixin` (`backend/app/database/repository/encrypted_columns.py`) does this for any repository that lists its `encrypted_columns`; it backs the per-credential `encrypted` flag on the API, the `GET /credentials/encryption` and `GET /datastores/encryption` status endpoints, and the `POST /credentials/reencrypt` and `POST /datastores/reencrypt` one-shot rewrites. A value that carries the prefix but cannot be decrypted raises `EncryptionKeyError`, which `main.py` maps to a 500 naming the key mismatch. See [Configuration](../getting-started/configuration.md) for setup.
