#!/bin/sh

# Script intented to be used as the entrypoint for the Docker container

# Run database migrations
uv run alembic upgrade head
# Start the FastAPI app
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --root-path /api
