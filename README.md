[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)

# Swarms Cloud
Infrastructure for scalable, reliable, and economical Multi-Modal Model API serving and deployment. We're using terraform to orchestrate infrastructure, FastAPI to host the models. If you're into deploying models for millions of people, join our discord and help contribute.


## Guides
- [Available Models](https://swarms.apac.ai/en/latest/swarms_cloud/available_models/)
- [Migrate from OpenAI to Swarms in 3 lines of code](https://swarms.apac.ai/en/latest/swarms_cloud/migrate_openai/)
- [Getting Started with SOTA Vision Language Models VLM](https://swarms.apac.ai/en/latest/swarms_cloud/getting_started/)
- [Enterprise Guide to High-Performance Multi-Agent LLM Deployments](https://swarms.apac.ai/en/latest/swarms_cloud/production_deployment/)


# Install
`pip install swarms-cloud`



## Architecture
user -> request -> load balanncer -> node[gpu] -> fast api -> model


## Scripts
`sky serve up -n [NAME] --cloud aws`


# Stack
- Backend: FastAPI
- Skypilot for container management
- Postresql for database
- Docker for cluster management
- Terraform


# License
MIT

## References
- [Noam tweet](https://x.com/NoamShazeer/status/1803790708358410380)
