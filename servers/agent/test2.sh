curl -X 'POST' \
  'http://127.0.0.1:8000/v1/agent/completions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "agent_name": "assistant",
  "system_prompt": "you are a large language model",
  "agent_description": "you are a large language model simulating a large language model",
  "model_name": "OpenAIChat",
  "max_loops": 1,
  "autosave": false,
  "dynamic_temperature_enabled": false,
  "dashboard": false,
  "verbose": true,
  "streaming_on": false,
  "saved_state_path": "assistant-save-state",
  "user_name": "User",
  "retry_attempts": 3,
  "task": "please make me a ham sammig"
}'
