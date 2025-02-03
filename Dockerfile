FROM python:3.11-slim

# Set environment variables to ensure Python output is logged and bytecode is not written
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Copy the requirements file first for dependency caching
COPY api/requirements.txt .


# Install build dependencies, then install Python dependencies, and finally remove build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apt-get purge -y --auto-remove gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy the API source code into the container
COPY api/ .

# Create a non-root user and change ownership of the application folder
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser /app
USER appuser


# Set Docker-related environment variables
ENV DOCKER_HOST=unix:///var/run/docker.sock
ENV DOCKER_TLS_VERIFY=0

# Expose port 80 for the application
EXPOSE 8080

# Start the API using Gunicorn with Uvicorn workers
CMD ["gunicorn", "api:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080"]
