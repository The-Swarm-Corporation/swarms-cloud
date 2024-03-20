#!/bin/bash

# Default values for environment variables
export MODEL_API_PORT=${MODEL_API_PORT:-8000}
export SERVER=${SERVER:-"http://localhost:${MODEL_API_PORT}"}
export USE_GPU=${USE_GPU:-True}
export WORLD_SIZE=${WORLD_SIZE:-4}
export PSG_CONNECTION_STRING=${PSG_CONNECTION_STRING:-""}
export COGVLM_MODEL_PATH=${COGVLM_MODEL_PATH:-"THUDM/cogvlm-chat-hf"}
export SUPABASE_URL=${SUPABASE_URL:-""}
export SUPABASE_KEY=${SUPABASE_KEY:-""}
export HF_HUB_ENABLE_HF_TRANSFER=${HF_HUB_ENABLE_HF_TRANSFER:-True}

# Run the application
exec python3.10 -m uvicorn cogvlm:app --host 0.0.0.0 --port $MODEL_API_PORT
