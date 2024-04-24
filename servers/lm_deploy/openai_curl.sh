#!/bin/sh

# Load environment variables from .env file
if [ -f .env ]; then
  export $(cat .env | xargs)
fi

# Get the model from environment variable
MODEL=$MODEL

# First run curl on v1/models to get available models
curl http://34.201.45.48:30002:8080/v1/models

# Run curl on v1/chat/completions with the specified model
curl http://34.201.45.48:30002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'$MODEL'",
    "messages": [{"role": "user", "content": "Hello! How are you?"}]
  }'
