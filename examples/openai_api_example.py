from openai import OpenAI

swarms_api_key = "sk-23232323"
swarms_base_url = "http://api.swarms.world/v1"
model = "internlm-xcomposer2-4khd-7b"

client = OpenAI(
    api_key=swarms_api_key,
    base_url=swarms_base_url,
)

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
