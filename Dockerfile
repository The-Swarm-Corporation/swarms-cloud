# Use the official PyTorch image as the base image
FROM nvcr.io/nvidia/pytorch:24.01-py3

# Set the working directory in the container
WORKDIR /app

# Copy the Python API script to the container
COPY api.py /app/api.py

# Copy the requirements file to the container
COPY requirements.txt /app/requirements.txt

# Set environment variables
ENV WORLD_SIZE=4
ENV ARTIFACTS_PATH=/app/artifacts
ENV STORAGE_PATH=/app/storage

# Run the command to download the requirements
RUN python -m pip install -r requirements.txt

# Set the entrypoint command for the container
CMD ["python", "api.py"]