import openai

# Set the API key
client = openai.OpenAI(
    # base_url="https://54.88.140.186:8000/v1", api_key="sk-1g3Z3y2c1f2z3d4b5p6w7c8b9v0n1m2"
    # base_url="https://18.223.159.245:8000/v1", api_key="sk-1g3Z3y2c1f2z3d4b5p6w7c8b9v0n1m2"
    # base_url="https://3.139.67.0:8000/v1", api_key="sk-1g3Z3y2c1f2z3d4b5p6w7c8b9v0n1m2"
    # base_url="https://18.212.172.250:8000/v1", api_key="sk-1g3Z3y2c1f2z3d4b5p6w7c8b9v0n1m2"
    # base_url="https://52.14.102.91:8000/v1", api_key="sk-1g3Z3y2c1f2z3d4b5p6w7c8b9v0n1m2"

    #  clusters
    # base_url="https://44.203.144.168:30001/v1", api_key="sk-1g3Z3y2c1f2z3d4b5p6w7c8b9v0n1m2"
    base_url="http://44.203.144.168:30002/v1", api_key="sk-1g3Z3y2c1f2z3d4b5p6w7c8b9v0n1m2"
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
