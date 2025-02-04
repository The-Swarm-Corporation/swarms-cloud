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
        print(agents)
        for agent in agents:
            print(agent)

        # Example: Creating a new agent
        new_agent_data = AgentCreate(
            name="ExampleAgent",
            description="A sample agent for demonstration.",
            code="def main(request, store):\n    return 'Hello, world!'",
            requirements="requests",
            autoscaling=False,
        )
        created_agent = client.create_agent(new_agent_data)
        print(f"Created agent: {created_agent}")
        print(created_agent.id)

        # # Run the agent
        # agent_id = created_agent.id
        # print(client.execute_agent(agent_id, {"input": "Hello, world!"}))

        # # Batch
        # print(
        #     client.batch_execute_agents(
        #         agent_id, [{"input": "Hello, world!"}, {"input": "Hello, world!"}]
        #     )
        # )

    except httpx.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logger.error(f"An unexpected error occurred: {err}")
