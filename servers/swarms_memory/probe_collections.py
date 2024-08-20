# Create a config
import requests

url = "https:35.222.137.183:30001/"

data = {"name": "my_collection"}

response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response JSON:", response.json())
