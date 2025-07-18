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
docker-compose up --build  # Start all services
docker-compose down       # Stop all services
```

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

## Code Conventions

Follow the guidelines in `CONVENTIONS.md`:
- Python: Use type hints, async/await, follow PEP 8
- JavaScript: Use Prettier defaults
- Keep functions small and focused
- Use meaningful variable names
- Handle errors with exceptions, not error codes