from openai import OpenAI

openai_api_key = "EMPTY"
import os
from dotenv import load_dotenv

load_dotenv()

openai_api_base = os.getenv("OPENAI_API_BASE")
model = os.getenv("MODEL")

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)
# Note that this model expects the image to come before the main text
chat_response = client.chat.completions.create(
    model=model,
    messages=[{
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
    }],
)
print("Chat response:", chat_response)