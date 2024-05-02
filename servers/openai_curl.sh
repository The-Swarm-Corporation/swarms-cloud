#!/bin/sh

# Load environment variables from .env file
if [ -f .env ]; then
  export $(cat .env | xargs)
fi

# Get the model from environment variable
MODEL=$MODEL

# First run curl on v1/models to get available models
curl -L $OPENAI_API_BASE/models && \

# Run curl on v1/chat/completions with the specified model
curl -L "$OPENAI_API_BASE/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'$MODEL'",
    "messages": [{"role": "user", "content": "Hello! How are you?"}]
  }'
