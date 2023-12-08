import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()


# Define the API endpoint
url = "http://localhost:8001/agent"

# Define the task for the agent
task = "Generate a 10,000 word blog on health and wellness."

# Define the payload for the POST request
payload = {
    "task": task,
}

# Send the POST request to the API
response = requests.post(url, data=json.dumps(payload))

# Print the response from the API
print(response.json())
