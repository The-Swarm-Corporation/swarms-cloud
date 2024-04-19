# Use the NVIDIA CUDA base image
FROM nvidia/cuda:12.1.1-devel-ubuntu22.04 as builder

# Set environment variables
ENV ARTIFACTS_PATH=/app/artifacts
ENV STORAGE_PATH=/app/storage
ENV HF_HUB_ENABLE_HF_TRANSFER=True

# Install Python 3.10 and other necessary system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    python3.10 python3.10-dev python3.10-distutils python3-pip python3.10-venv openmpi-bin libopenmpi-dev \
    && python3.10 -m pip install --no-cache-dir --upgrade pip setuptools wheel \
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
    && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list \
    && sudo apt-get install -y nvidia-container-toolkit \
    
WORKDIR /swarms-cloud

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install Python dependencies from requirements.txt
RUN python3.10 -m pip install -r requirements.txt \
EXPOSE 8000

ENTRYPOINT ["/opt/nvidia/nvidia_entrypoint.sh"]
# Run the cogvlm.py file as a Uvicorn server on port 8000
CMD ["uvicorn", "cogvlm:app", "--host", "0.0.0.0", "--port", "8000"]
