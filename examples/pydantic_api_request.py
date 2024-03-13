from pydantic import BaseModel, Field
from typing import List, Dict, Any
import requests
import base64
from PIL import Image
from io import BytesIO

# Single BaseModel for the entire API request structure
class APIRequest(BaseModel):
    model: str
    messages: List[Dict[str, Any]]
    temperature: float
    top_p: float
    max_tokens: int

# Convert image to Base64
def image_to_base64(image_path: str) -> str:
    with Image.open(image_path) as image:
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

# Replace 'image.jpg' with the path to your image
base64_image = image_to_base64("image.jpg")

# Construct the request data
request_data = APIRequest(
    model="cogvlm-chat-17b",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe what is in the image"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
            ]
        }
    ],
    temperature=0.8,
    top_p=0.9,
    max_tokens=1024
)

# Specify the URL of your FastAPI application
url = "https://api.swarms.world/v1/chat/completions"

# Send the request
response = requests.post(url, json=request_data.dict())
# Print the response from the server
print(response.text)
