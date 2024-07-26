curl -X 'POST' \
  'http://127.0.0.1:8000/v1/agent/completions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "agent_name": "Swarm Agent",
  "system_prompt": "string",
  "agent_description": "string",
  "model_name": "OpenAIChat",
  "max_loops": 1,
  "autosave": false,
  "dynamic_temperature_enabled": false,
  "dashboard": false,
  "verbose": false,
  "streaming_on": true,
  "saved_state_path": "string",
  "sop": "string",
  "sop_list": [
    "string"
  ],
  "user_name": "User",
  "retry_attempts": 3,
  "context_length": 8192,
  "task": "string"
}'
