import requests
import base64
import json
from PIL import Image
from io import BytesIO

# Convert image to Base64
def image_to_base64(image_path):
    with Image.open(image_path) as image:
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

# Replace 'image.jpg' with the path to your image
base64_image = image_to_base64('images/3897e80dcb0601c0.jpg')
image_data = {
    "type": "image_url",
    "image_url": {
        "url": f"data:image/jpeg;base64,{base64_image}"
    }
}

# Construct the request data
request_data = {
    "model": "cogvlm-chat-17b", # Replace with your model's name
    "messages": [
        {
            "role": "user",
            "content": [{"type":"text","text":"Describe the image"},image_data] # This could include text and/or other images
        }
    ],
    "temperature": 0.8,
    "top_p": 0.9,
    "max_tokens": 1024
}

# Specify the URL of your FastAPI application
url = 'http://ec2-3-83-148-203.compute-1.amazonaws.com:8000/v1/chat/completions'

# Send the request
response = requests.post(url, json=request_data)

# Print the response from the server
print(response.text)
