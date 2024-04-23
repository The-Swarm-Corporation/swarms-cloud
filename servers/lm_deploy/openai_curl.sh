#!/bin/sh

curl http://34.201.45.48:30001/v1/chat/completions \
# curl http://34.201.45.48:30002/v1/chat/completions \
# curl http://34.201.45.48:30003/v1/chat/completions \
# curl http://https://18.118.142.150:8080/v1/chat/completions \
# curl http://18.191.186.173:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "xtuner/llava-llama-3-8b-v1_1",
    # "model": "xtuner/llava-llama-3-8b-v1_1",
    # "model": "xtuner/llava-llama-3-8b-v1_1",
    "messages": [{"role": "user", "content": "Hello! How are you?"}]
  }'
