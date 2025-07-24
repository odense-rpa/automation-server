# Use the official Python image from the Docker Hub
FROM python:3.13-slim

# Install uv and uvx
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy the FastAPI app code and entry-point script
COPY . /app
COPY ./alembic.ini.docker /app/alembic.ini
COPY scripts/entry-point.sh /app/entry-point.sh

RUN rm -f .env

RUN uv sync

# Make the entry-point script executable
RUN chmod +x /app/entry-point.sh

# Create a directory for the SQLite database
RUN mkdir /data

# Set environment variables
ENV DEBUG=False
ENV DATABASE_URL="sqlite:////data/automationserver.db"

# Expose the port FastAPI runs on
EXPOSE 8000

# Use the entry-point script to run the app
ENTRYPOINT ["/app/entry-point.sh"]
