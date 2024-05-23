from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
openai_api_key = "sk-9c34d01b0095c16b987d925402fb283972ec64548828ca8ae321930e4c45745d"

openai_api_base = "https://api.swarms.world/v1"
model = "Meta-Llama-3-8B-Instruct"

client = OpenAI(api_key=openai_api_key, base_url=openai_api_base)
# Note that this model expects the image to come before the main text
chat_response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
            ],
        }
    ],
    temperature=0.1,
    max_tokens=3400,
)
print("Chat response:", chat_response)
