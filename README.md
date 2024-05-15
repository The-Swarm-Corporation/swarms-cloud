[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)

# Swarms Cloud
Infrastructure for scalable, reliable, and economical Multi-Modal Model API serving and deployment. We're using terraform to orchestrate infrastructure, FastAPI to host the models. If you're into deploying models for millions of people, join our discord and help contribute.


# Install
`pip install swarms-cloud`



## Architecture
user -> request -> load balanncer -> node[gpu] -> fast api -> model




## Calculate Pricing
```python
from transformers import AutoTokenizer
from swarms_cloud import calculate_pricing

# Initialize the tokenizer
tokenizer = AutoTokenizer.from_pretrained("gpt2")

# Define the example texts
texts = ["This is the first example text.", "This is the second example text."]

# Calculate pricing and retrieve the results
total_tokens, total_sentences, total_words, total_characters, total_paragraphs, cost = calculate_pricing(texts, tokenizer)

# Print the total tokens processed
print(f"Total tokens processed: {total_tokens}")

# Print the total cost
print(f"Total cost: ${cost:.5f}")
```


## Generate an API key
```python
from swarms_cloud.api_key_generator import generate_api_key

out = generate_api_key(prefix="sk", length=30)

print(out)

```

# Stack
- Backend: FastAPI
- Skypilot for container management
- Stripe for payment tracking
- Postresql for database
- TensorRT for inference
- Docker for cluster management
- Kubernetes for managing and autoscaling docker containers
- Terraform


# License
MIT
