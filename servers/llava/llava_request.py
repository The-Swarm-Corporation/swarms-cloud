import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
openai_api_key = "EMPTY"

openai_api_base = os.getenv("OPENAI_API_BASE", "http://34.201.45.48:30002/v1")
model = os.getenv("MODEL", "llava")

client = OpenAI(api_key="sk-23232323", base_url=openai_api_base, timeout=500)
# Note that this model expects the image to come before the main text
chat_response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
                    },
                },
                {"type": "text", "text": "What's in this image?"},
            ],
        }
    ],
)
print("Chat response:", chat_response)
