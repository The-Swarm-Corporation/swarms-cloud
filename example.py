import asyncio
import base64
from io import BytesIO

import httpx
from httpx import Timeout
from PIL import Image


# Convert image to Base64
async def image_to_base64(image_path):
    with Image.open(image_path) as image:
        buffered = BytesIO()
        image.save(buffered, format="JPEG", quality=85)
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str


async def send_request(base64_image):
    text_data = {"type": "text", "text": "Describe what is in the image"}
    image_data = {
        "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
    }

    # Construct the request data
    request_data = {
        "model": "cogvlm-chat-17b",
        "messages": [{"role": "user", "content": [text_data, image_data]}],
        "temperature": 0.8,
        "top_p": 0.9,
        "max_tokens": 1024,
    }

    # Specify the URL of your FastAPI application
    url = "https://api.swarms.world/v1/chat/completions"

    # Timeout
    timeout = Timeout(10.0, read=30.0)

    # Use httpx.AsyncClient for asynchronous requests
    async with httpx.AsyncClient(timeout=timeout, http2=True) as client:
        response = await client.post(url, json=request_data)
        print(response.text)


async def main():
    # Replace 'image.jpg' with the path to your image
    base64_image = await image_to_base64("test.jpg")
    await send_request(base64_image)


if __name__ == "__main__":
    asyncio.run(main())
