import httpx
from swarms_cloud.main import AgentCreate, SwarmCloudAPI
from loguru import logger

if __name__ == "__main__":
    # Example: Using the client in a script
    try:
        client = SwarmCloudAPI
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
            requirements="",
            envs="",
            autoscaling=False,
        )
        created_agent = client.create_agent(new_agent_data)
        print(f"Created agent: {created_agent}")

    except httpx.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logger.error(f"An unexpected error occurred: {err}")
    finally:
        client.close()
