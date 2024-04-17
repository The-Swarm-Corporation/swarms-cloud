import requests
import json

url = "http://localhost:8000/v1/chat/completions"
headers = {"Content-Type": "application/json"}
data = {
    "model_name": "ByteDance/AnimateDiff-Lightning",
    "task": "Beautiful girl studying with hijab",
    "resolution": "720",
    "length": 60,
    "style": "example_style",
    "n": 1,
    "output_type": ".gif",
    "output_path": "animate.gif",
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.json())
