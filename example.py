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
