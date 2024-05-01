from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
openai_api_key = "sk-31ef079e2030efcc48fe675a73fb9e76f5db49f141f3f4d79c0339d1b770b5e8"

openai_api_base = "https://api.swarms.world"
model = "llama3"

client = OpenAI(api_key=openai_api_key, base_url=openai_api_base, timeout=30)
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
                        "url": "https://home-cdn.reolink.us/wp-content/uploads/2022/04/010345091648784709.4253.jpg",
                    },
                },
                {"type": "text", "text": "What's in this image?"},
            ],
        }
    ],
    temperature=0.1,
)
print("Chat response:", chat_response)
