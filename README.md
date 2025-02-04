
# Swarms Cloud: Revolutionize Automation with Agentic APIs


[![Join our Discord](https://img.shields.io/badge/Discord-Join%20our%20server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/swarms) [![Subscribe on YouTube](https://img.shields.io/badge/YouTube-Subscribe-red?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@kyegomez3242) [![Connect on LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kye-g-38759a207/) [![Follow on X.com](https://img.shields.io/badge/X.com-Follow-1DA1F2?style=for-the-badge&logo=x&logoColor=white)](https://x.com/kyegomezb)

Welcome to Swarms Cloud, the ultimate platform for deploying, managing, and monetizing intelligent agents. With Swarms Cloud, you can seamlessly create and publish agents that perform a wide range of automated tasks, allowing businesses and developers to integrate agentic intelligence into their workflows. This guide will help you get started with Swarms Cloud quickly and easily.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Creating and Publishing Agents](#creating-and-publishing-agents)
- [Managing Your Agents](#managing-your-agents)
- [Monetizing Agents](#monetizing-agents)
- [Contributing](#contributing)
- [License](#license)

---


## Overview

**Swarms Cloud** enables developers and businesses to publish, manage, and monetize agentic APIs on a global marketplace. The Swarms platform simplifies complex automation tasks, making agents easy to discover, integrate, and scale across industries.

By leveraging the **Swarms CLI**, you can publish agents in just a few commands, set custom pricing models, and generate revenue from your intelligent agents as they are integrated by businesses around the world.

### Key Benefits:

- **Seamless Publishing**: Deploy agents to the marketplace using our CLI in a few simple steps.
- **Monetization**: Set custom pricing and licensing options for your agents, and create sustainable income streams.
- **Global Marketplace**: Allow businesses and developers to discover, test, and integrate your agents into their workflows.
- **Streamlined Agent Management**: Monitor and manage your agents using the Swarms Cloud Dashboard.

---

## Features

- **Agent Publishing**: Deploy agents directly from your development environment using the Swarms CLI.
- **Marketplace Integration**: Showcase your agents in a global marketplace for businesses to integrate.
- **Revenue Generation**: Monetize your agent APIs through flexible pricing models.
- **API Metrics & Monitoring**: Track API usage and performance with real-time data.
- **Subscription & Licensing Models**: Offer various monetization strategies like pay-per-use or subscriptions.
- **Easy Integration**: Businesses can easily integrate agentic intelligence into their workflows with minimal setup.

---

## Installation

To install the **Swarms Cloud** Python package, simply use the following command:

```bash
pip install -U swarms-cloud
```

## Usage

```python
import httpx
from swarms_cloud.main import AgentCreate, SwarmCloudAPI
from loguru import logger
import os

if __name__ == "__main__":
    # Example: Using the client in a script
    try:
        client = SwarmCloudAPI(api_key=os.getenv("SWARMS_API_KEY"))
        logger.info("Checking API health...")
        print(client.health())

        logger.info("Listing agents...")
        agents = client.list_agents()
        for agent in agents:
            print(agent)

        # Example: Creating a new agent
        new_agent_data = AgentCreate(
            name="ExampleAgent",
            description="A sample agent for demonstration.",
            code="def main(request, store):\n    return 'Hello, world!'",
            requirements="requests",
            envs="",
            autoscaling=False,
        )
        created_agent = client.create_agent(new_agent_data)
        print(f"Created agent: {created_agent}")

        # # Execute the agent
        # execution = client.execute_agent(created_agent.id, {"input": "Hello, world!"})
        # print(f"Execution: {execution}")

        # # Run the agent
        # agent_id = created_agent.id
        # agent_run = client.run_agent(agent_id)
        # print(f"Agent run: {agent_run}")

    except httpx.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logger.error(f"An unexpected error occurred: {err}")
```
---

## Managing Your Agents

Once your agent is published, you can monitor its performance and usage via the **Swarms Cloud Dashboard**. Here are some of the key management features:

- **API Usage Analytics**: Track the number of API calls, users, and income generated.
- **Pricing Adjustments**: Update the pricing or subscription model for your agent at any time.
- **Version Control**: Manage different versions of your agent and roll out updates seamlessly.
- **Licensing Options**: Choose between subscription-based models, pay-per-use, or full-access licensing.

---

## Contributing

We welcome contributions to **Swarms Cloud**! Whether you're fixing bugs, adding new features, or improving documentation, your input is valuable to the community.

To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/new-feature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/new-feature`).
5. Create a pull request.

For more detailed information, please refer to our [Contribution Guidelines](CONTRIBUTING.md).

---

## License

**Swarms Cloud** is released under the [MIT License](LICENSE).

---

For more information, visit our official [Swarms Cloud Documentation](https://docs.swarms.world).

