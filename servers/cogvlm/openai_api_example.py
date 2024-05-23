import openai

# Set the API key
client = openai.OpenAI(
    #  clusters
    # base_url="https://44.203.144.168:30001/v1", api_key="sk-1g3Z3y2c1f2z3d4b5p6w7c8b9v0n1m2"
    base_url="http://40.87.83.103:30001/v1",
    api_key="sk-1g3Z3y2c1f2z3d4b5p6w7c8b9v0n1m2",
    # base_url="https://18.189.185.191:8000/v1", api_key="sk-1g3Z3y2c1f2z3d4b5p6w7c8b9v0n1m2"
)
# Create a client object to interact with the OpenAI API
# Make a chat completion request
chat_completion = client.chat.completions.create(
    model="cogvlm-chat-17b",
    messages=[{"role": "user", "content": "Write me a love song"}],
    temperature=0.7,
)

# Send a message to the chat model and get a completion response
