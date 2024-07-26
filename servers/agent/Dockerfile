# Use the official lightweight Python image.
FROM python:3.11-slim

# Set environment variables to prevent Python from writing pyc files to disc and to prevent it from buffering stdout and stderr.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and set the working directory
WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI application code
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--access-log",     "--no-use-colors",  "--log-level", "trace"]

# Additional optimizations:
# 1. Use multi-stage builds to separate the build environment from the runtime environment if necessary.
# 2. Minimize the number of layers by chaining RUN commands.
# 3. Use .dockerignore to exclude unnecessary files from the image.
