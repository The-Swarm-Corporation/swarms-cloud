import requests
import json

url = "http://127.0.0.1:8000/v1/agent/completions"

data = {
    "agent_name": "Financial Assistant",
    "system_prompt": "You are a financial assistant. Help users with their financial queries.",
    "model_name": "OpenAIChat",
    "max_loops": 1,
    "autosave": False,
    "dynamic_temperature_enabled": False,
    "dashboard": False,
    "verbose": True,
    "streaming_on": False,
    "user_name": "User",
    "retry_attempts": 3,
    "context_length": 8192,
    "task": "What is the current exchange rate for USD to EUR?",
    "max_tokens": 100,
    "tool_schema": None
}

headers = {'Content-Type': 'application/json'}

response = requests.post(url, data=json.dumps(data), headers=headers)

print(response)
print(response.content)
