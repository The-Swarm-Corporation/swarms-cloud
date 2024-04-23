curl -L 40.87.83.103:30001/v1/chat/completions \
    -X POST \
    -d '{"model": "mistralai/Mixtral-8x7B-Instruct-v0.1", "messages": [{"role": "user", "content": "Who are you?"}]}' \
    -H 'Content-Type: application/json'
