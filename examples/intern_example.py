from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
openai_api_key = "sk-c6e623fb53b21c96c2545e9683166896107640e7c0382dcd7b7334ae9046eb18"

openai_api_base = "https://api.swarms.world/v1"
model = "internlm-xcomposer2-4khd"

client = OpenAI(api_key=openai_api_key, base_url=openai_api_base)
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
                {
                    "type": "text",
                    "text": "What is the most dangerous object in the image?",
                },
            ],
        }
    ],
    temperature=0.1,
    max_tokens=5000,
)
print("Chat response:", chat_response)
