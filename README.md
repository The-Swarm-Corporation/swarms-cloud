[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)

# Swarms Cloud

[![Join our Discord](https://img.shields.io/badge/Discord-Join%20our%20server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/agora-999382051935506503) [![Subscribe on YouTube](https://img.shields.io/badge/YouTube-Subscribe-red?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@kyegomez3242) [![Connect on LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kye-g-38759a207/) [![Follow on X.com](https://img.shields.io/badge/X.com-Follow-1DA1F2?style=for-the-badge&logo=x&logoColor=white)](https://x.com/kyegomezb)

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
