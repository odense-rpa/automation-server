# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI app code
COPY . /app

# Create a directory for the SQLite database
RUN mkdir /data

# Set environment variables
ENV DEBUG=False
ENV DATABASE_URL="sqlite:///data/automationserver.db"

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the FastAPI app with uvicorn
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
