#!/bin/sh

# Script intented to be used as the entrypoint for the Docker container

# Run database migrations
alembic upgrade head
# Start the FastAPI app
uvicorn app.app:app --host 0.0.0.0 --port 8000
