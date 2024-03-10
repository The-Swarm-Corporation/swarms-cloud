import requests
import base64
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
# Construct the request data
request_data = {
    "model": "cogvlm-chat-17b",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "Whats in this image?"
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
            }
        ]
        }
    ],
    "temperature": 0.8,
    "top_p": 0.9,
    "max_tokens": 1024,
}

# Specify the URL of your FastAPI application
url = 'http://localhost:8000/v1/chat/completions'

# Send the request
response = requests.post(url, json=request_data)
# Print the response from the server
print(response.text)
