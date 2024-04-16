curl -L 34.205.144.249:30001/v1/chat/completions \
    -X POST \
    -d '{"model": "mistralai/Mixtral-8x7B-Instruct-v0.1", "messages": [{"role": "user", "content": "Who are you?"}]}' \
    -H 'Content-Type: application/json'
