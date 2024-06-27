import openai

# Set the API key
client = openai.OpenAI(
    #  clusters
    # base_url="https://44.203.144.168:30001/v1", api_key=""
    base_url="http://40.87.83.103:30001/v1",
    api_key="",
    # base_url="https://18.189.185.191:8000/v1", api_key=""
)
# Create a client object to interact with the OpenAI API
# Make a chat completion request
chat_completion = client.chat.completions.create(
    model="cogvlm-chat-17b",
    messages=[{"role": "user", "content": "Write me a love song"}],
    temperature=0.7,
)

# Send a message to the chat model and get a completion response
