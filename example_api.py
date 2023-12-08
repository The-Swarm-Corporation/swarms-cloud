import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()


# Get the API key from the environment
api_key = os.getenv("OPENAI_API_KEY")

# Define the API endpoint
url = "http://localhost:8000/agent"

# Define the input parameters for the agent
agent_parameters = {
    "temperature": 0.5,
    "model_name": "gpt-4",
    "openai_api_key": api_key,
    "max_loops": 1,
    "autosave": True,
    "dashboard": True,
}

# Define the task for the agent
task = "Generate a 10,000 word blog on health and wellness."

# Define the payload for the POST request
payload = {
    "task": task,
    "parameters": agent_parameters,
    "args": [],  # Add your args here
    "kwargs": {},  # Add your kwargs here
}

# Send the POST request to the API
response = requests.post(url, data=json.dumps(payload))

# Print the response from the API
print(response.json())
