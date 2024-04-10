# Use an official Python runtime as a parent image, compatible with the requirements
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    gcc \
    libssl-dev \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Rust, which is required for some dependencies
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Ensure Rust binaries are in the PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Protoc
RUN PROTOC_ZIP=protoc-21.12-linux-x86_64.zip \
    && curl -OL https://github.com/protocolbuffers/protobuf/releases/download/v21.12/$PROTOC_ZIP \
    && unzip -o $PROTOC_ZIP -d /usr/local bin/protoc \
    && unzip -o $PROTOC_ZIP -d /usr/local 'include/*' \
    && rm -f $PROTOC_ZIP

# Clone the text-generation-inference repository and install its dependencies
RUN git clone https://github.com/huggingface/text-generation-inference.git && cd text-generation-inference \
    && BUILD_EXTENSIONS=True make install \
    && cd ..

# Set the environment variable for the model ID
ENV MODEL=HuggingFaceM4/idefics-80b

# Expose the port the app will run on
ENV PORT 8000
EXPOSE 8000

# Define an entry point script to initialize the model serving
# Adjust the command to match the specific volume and model usage
ENTRYPOINT ["sh", "-c", "text-generation-launcher --model-id ${MODEL} --port ${PORT}"]

# The Docker run command from the user will specify the GPU settings, shared memory size, port mapping, and volume mapping
# Example Docker run command provided by the user, adjusted for clarity and to match the Dockerfile's settings:
# docker run --gpus all --shm-size 1g -p $PORT:80 -v $volume:/data ghcr.io/huggingface/text-generation-inference:1.4 --model-id $MODEL