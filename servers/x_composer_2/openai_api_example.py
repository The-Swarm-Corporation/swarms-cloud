from openai import OpenAI

openai_api_key = "sk-23232323"
openai_api_base = "http://199.204.135.78:23333/v1"
model = "internlm-xcomposer2-4khd-7b"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
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
