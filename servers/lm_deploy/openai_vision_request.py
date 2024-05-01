from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
openai_api_base = os.getenv("OPENAI_API_BASE")
openai_api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("MODEL")

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

try:
    chat_response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "user",
            "content": {
                "type": "image_url",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
            },
            "role": "user",
            "content": {
                "type": "text",
                "text": "What is in the image "
            }
        }],
    )
    print("Chat response:", chat_response)
except Exception as e:
    print(f"An error occurred: {e}")
