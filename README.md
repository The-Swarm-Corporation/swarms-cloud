[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)

# Swarms Cloud
Infrastructure for scalable, reliable, and economical Multi-Modal Model API serving and deployment. We're using terraform to orchestrate infrastructure, FastAPI to host the models. If you're into deploying models for millions of people, join our discord and help contribute.


# Install
`pip install swarms-cloud`



## Architecture
user -> request -> load balanncer -> node[gpu] -> fast api -> model


## Scripts
`sky serve up -n [NAME] --cloud aws`

## Guides
- [Available Models](https://swarms.apac.ai/en/latest/swarms_cloud/available_models/)
- [Migrate from OpenAI to Swarms in 3 lines of code](https://swarms.apac.ai/en/latest/swarms_cloud/migrate_openai/)
- [Getting Started with SOTA Vision Language Models VLM](https://swarms.apac.ai/en/latest/swarms_cloud/getting_started/)
- [Enterprise Guide to High-Performance Multi-Agent LLM Deployments](https://swarms.apac.ai/en/latest/swarms_cloud/production_deployment/)


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
