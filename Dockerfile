# Use an NVIDIA CUDA base image with Python 3.10
FROM nvidia/cuda:12.1.1-devel-ubuntu22.04 as builder

# Set environment variables to make Python 3.10 as the default version
ENV BASE_IMG=nvidia/cuda:12.1.1-devel-ubuntu22.04

# Install Python 3.10 and other necessary system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    python3.10 python3.10-dev python3.10-distutils python3-pip python3.10-venv openmpi-bin libopenmpi-dev \
    libopenmpi-dev \
    && python3.10 -m pip install --no-cache-dir --upgrade pip setuptools wheel


# Set the working directory
WORKDIR /

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install Python dependencies from requirements.txt, taking into account the custom PyPI repositories
RUN pip install -r requirements.txt

# Copy the rest of your application's code into the container
COPY . /swarms_root
WORKDIR /swarm_root/servers

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python3.10", "-m", "uvicorn", "servers/cogvlm:main", "--host", "0.0.0.0", "--port", "8000"]
