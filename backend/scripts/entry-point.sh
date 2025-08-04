#!/bin/sh

set -e  # Exit on error

# Script intended to be used as the entrypoint for the Docker container

echo "Starting Automation Server Backend..."

# Run database migrations
echo "Running database migrations..."
if uv run alembic upgrade head; then
    echo "Database migrations completed successfully"
else
    echo "ERROR: Database migrations failed" >&2
    exit 1
fi

# Start the FastAPI app
echo "Starting FastAPI application..."
exec uv run uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --root-path /api \
    --proxy-headers \
    --forwarded-allow-ips="*"