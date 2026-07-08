# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automation Server is a Python-based automation platform with three main components:
- **Backend**: FastAPI-based REST API with PostgreSQL database
- **Frontend**: Vue.js 3 web interface with Tailwind CSS and DaisyUI
- **Worker**: Python script execution environment

The system is designed to run in Docker containers and manages automation scripts through a web interface.

## Architecture

The system follows a modular architecture:
- **API Layer**: FastAPI routers handle HTTP requests
- **Service Layer**: Business logic and orchestration
- **Repository Layer**: Data access with SQLModel ORM
- **Database**: PostgreSQL

Key directories:
- `backend/app/api/v1/`: API endpoints and routers
- `backend/app/services/`: Business logic services
- `backend/app/database/`: Models, repositories, and database session management
- `backend/app/scheduler/`: Modular scheduler implementation
- `frontend/src/components/`: Vue components
- `frontend/src/views/`: Vue page views
- `worker/`: Script execution environment

## Development Commands

### Backend (Python)
```bash
cd backend
uv sync                    # Install dependencies
uv run uvicorn app.main:app --reload  # Run development server
uv run pytest             # Run tests
uv run alembic upgrade head  # Run database migrations
```

### Frontend (Vue.js)
```bash
cd frontend
npm install               # Install dependencies
npm run dev              # Run development server
npm run build            # Build for production
npm run lint             # Run ESLint
npm run format           # Format code with Prettier
```

### Docker Development
```bash
docker compose up --build        # Start all services (auto-applies override)
docker compose --profile tools up  # Include optional dev tools (Adminer)
docker compose down              # Stop all services
```

For production:
```bash
docker compose -f docker-compose.yml up -d  # Production only (no override)
```

File structure:
- `docker-compose.yml` — production base (GHCR images, no defaults)
- `docker-compose.override.yml` — development overrides (auto-applied by `docker compose up`)

## Git Workflow

Trunk-based development. `main` is the only long-lived branch; releases
are marked by `v*` tags.

- Never commit directly to `main`. Branch protection requires a PR with
  green CI; admins are exempt from the rule — do not use that bypass.
- Branch from `main`, open PR against `main`, merge when CI is green,
  delete the branch after merge.
- PRs behind `main` must be updated before merging (strict rule):
  `gh pr update-branch <PR>`.
- Commit messages: Conventional Commits (`feat:`, `fix:`, `chore:`,
  `docs:`, `ci:`, `test:`).

### CI checks (required to merge)

`.github/workflows/ci.yml` runs two jobs on every PR. Reproduce locally
before pushing:

```bash
# backend job
cd backend && uv run ruff check . && uv run pytest

# frontend job — use raw eslint, NOT `npm run lint` (that script passes
# --fix and mutates files instead of failing)
cd frontend && npx eslint . --ext .vue,.js,.jsx,.cjs,.mjs --ignore-path .gitignore && npm run build
```

CI pins Python 3.13 — Python 3.14 breaks the psycopg2-binary build.
Use `uv run --python 3.13` locally if your default is newer.

### Releases

```bash
./scripts/release.sh X.Y.Z   # run on main with a clean tree
```

The script bumps versions across all files (via `bump-version.sh`),
commits, tags `vX.Y.Z`, and pushes; the tag triggers Docker image
builds to GHCR. Never bump version numbers by hand. Nightly images
build from `main` at 02:00 UTC.

## Database Operations

- Database is PostGresql
- Migrations are handled by Alembic
- Database models are in `backend/app/database/models.py`

## Testing

Backend tests use pytest and are located in `backend/tests/`. Tests cover:
- API endpoints
- Services
- Repository patterns
- Database operations

Run tests with: `cd backend && uv run pytest`

## Scheduler Architecture

The scheduler has been refactored into a modular architecture using the Strategy pattern:

### Structure
```
backend/app/scheduler/
├── __init__.py              # Package exports and documentation
├── core.py                  # Main AutomationScheduler class
├── validators.py            # Parameter and cron validation
├── dispatcher.py            # Resource allocation logic
├── utils.py                # Utility functions for resource matching
└── trigger_processors/     # Strategy pattern implementation
    ├── __init__.py
    ├── base.py             # AbstractTriggerProcessor interface
    ├── cron.py             # Cron trigger processor
    ├── date.py             # Date trigger processor
    ├── workqueue.py        # Workqueue trigger processor
    └── registry.py         # Processor registry
```

### Key Components

- **AutomationScheduler**: Main orchestrator that manages the scheduling loop
- **TriggerProcessors**: Handle specific trigger types using the Strategy pattern
- **ResourceDispatcher**: Manages session-to-resource allocation
- **ProcessingServices**: Container for dependency injection of services and repositories
- **TriggerProcessorRegistry**: Maps trigger types to their processors

### Adding New Trigger Types

1. Create a new processor class inheriting from `AbstractTriggerProcessor`
2. Implement the `_process_trigger` method with your specific logic
3. Register the processor in `TriggerProcessorRegistry`
4. Add the new trigger type to the `TriggerType` enum

### Testing

Scheduler tests are located in `backend/tests/scheduler/` with comprehensive coverage:
- Unit tests for each trigger processor
- Integration tests for the core scheduler
- Validation and utility function tests

## Key Configuration

- Backend config: `backend/app/config.py`
- Database URL: Set via `DATABASE_URL` environment variable
- Frontend API base URL: Set via `VITE_ATS_API_BASE_URL`

## Frontend Notes

- Icons use `@fortawesome/vue-fontawesome` with explicit registration — **not** CSS webfonts. New icons must be imported and added to `library.add()` in `frontend/src/fontAwesome.js`, then used as `<font-awesome-icon :icon="['fas', 'icon-name']" />`. Do not use `<i class="fa fa-...">`.
- Vue components use Options API (not Composition API)

## Code Conventions

Follow the guidelines in `CONVENTIONS.md`:
- Python: Use type hints, async/await, follow PEP 8
- JavaScript: Use Prettier defaults
- Keep functions small and focused
- Use meaningful variable names
- Handle errors with exceptions, not error codes