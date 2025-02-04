#!/usr/bin/env python
"""
SwarmCloudAPI Client
--------------------

A production-grade client for interacting with the SwarmCloud Agent API. This client
provides methods for listing, creating, updating, executing, and fetching the execution
history of agents. It leverages httpx for HTTP communication, pydantic for data validation,
and loguru for logging.

Usage:
    >>> from swarmcloud_api_client import SwarmCloudAPI, AgentCreate, AgentUpdate, ExecutionPayload
    >>>
    >>> # Instantiate the client with the API base URL and your API key.
    >>> client = SwarmCloudAPI(base_url="http://localhost:8080", api_key="your_api_key_here")
    >>>
    >>> # List agents
    >>> agents = client.list_agents()
    >>> print(agents)
    >>>
    >>> # Create an agent
    >>> agent_data = AgentCreate(
    ...     name="TranslateAgent",
    ...     description="An agent that translates text",
    ...     code="def main(request, store):\n    text = request.payload.get('text', '')\n    return f'Translated: {text}'",
    ...     requirements="requests==2.25.1",
    ...     envs="DEBUG=True",
    ...     autoscaling=False
    ... )
    >>> new_agent = client.create_agent(agent_data)
    >>> print(new_agent)
    >>>
    >>> # Clean up the client
    >>> client.close()
"""

import os
from typing import Any, Dict, List, Optional
import uuid

import httpx
from loguru import logger
from pydantic import BaseModel, Field
from datetime import datetime


# ------------------------------------------------------------------------------
# Pydantic Models corresponding to the API's data structures
# ------------------------------------------------------------------------------


def generate_id():
    return str(uuid.uuid4())


unique_id = generate_id()


class AgentBase(BaseModel):
    id: str = Field(default=unique_id, example="123")
    name: str = Field(..., example="TranslateAgent")
    description: Optional[str] = Field(None, example="An agent that translates text")
    code: str = Field(
        ...,
        example=(
            "def main(request, store):\n"
            "    text = request.payload.get('text', '')\n"
            "    return f'Translated: {text}'\n"
        ),
    )
    requirements: Optional[str] = Field(None, example="requests==2.25.1")
    envs: Optional[str] = Field(None, example="DEBUG=True")
    creator: Optional[str] = Field(default=unique_id, example="123")


class AgentCreate(AgentBase):
    autoscaling: Optional[bool] = Field(
        False,
        description="If true, the system will allow the agent to scale its executions concurrently.",
    )


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    requirements: Optional[str] = None
    autoscaling: Optional[bool] = None


class AgentOut(AgentBase):
    id: str
    created_at: datetime
    autoscaling: bool = False


class ExecutionPayload(BaseModel):
    payload: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ExecutionLog(BaseModel):
    timestamp: datetime
    log: str


class AgentExecutionHistory(BaseModel):
    agent_id: str
    executions: List[ExecutionLog]


# ------------------------------------------------------------------------------
# SwarmCloudAPI Client Implementation
# ------------------------------------------------------------------------------


class SwarmCloudAPI:
    """
    Client for interacting with the SwarmCloud Agent API.

    Attributes:
        base_url (str): The base URL of the API.
        api_key (str): The API key used for authentication.
        timeout (float): Request timeout in seconds.
    """

    def __init__(
        self,
        base_url: str = "https://swarmcloud-285321057562.us-central1.run.app",
        api_key: str = os.getenv("SWARMS_API_KEY"),
        timeout: float = 10.0,
    ) -> None:
        """
        Initialize the client.

        Args:
            base_url (str): The API's base URL (e.g., "http://localhost:8080").
            api_key (str): The API key to be included in request headers.
            timeout (float, optional): Timeout for HTTP requests. Defaults to 10.0 seconds.
        """
        try:
            self.base_url = base_url.rstrip("/")
            self.api_key = api_key
            self.timeout = timeout
            self.headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
            }
            self.client = httpx.Client(
                base_url=self.base_url, headers=self.headers, timeout=self.timeout
            )
            logger.info(
                f"SwarmCloudAPI client initialized with base URL: {self.base_url}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize SwarmCloudAPI client: {str(e)}")
            raise

    def close(self) -> None:
        """
        Close the underlying HTTP client.
        """
        try:
            self.client.close()
            logger.info("SwarmCloudAPI client closed.")
        except Exception as e:
            logger.error(f"Error closing SwarmCloudAPI client: {str(e)}")
            raise

    def list_agents(self) -> List[AgentOut]:
        """
        Retrieve all agents.

        Returns:
            List[AgentOut]: A list of agents.

        Raises:
            httpx.HTTPError: If the HTTP request fails.
        """
        try:
            endpoint = "/agents"
            logger.debug(f"Requesting list of agents from {endpoint}")
            response = self.client.get(endpoint)
            response.raise_for_status()
            agents_data = response.json()
            agents = [AgentOut.parse_obj(agent) for agent in agents_data]
            logger.info(f"Retrieved {len(agents)} agents.")
            return agents
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while listing agents: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while listing agents: {str(e)}")
            raise

    def create_agent(self, agent: AgentCreate) -> AgentOut:
        """
        Create a new agent.

        Args:
            agent (AgentCreate): The agent data to create.

        Returns:
            AgentOut: The created agent's data.

        Raises:
            httpx.HTTPError: If the HTTP request fails.
        """
        try:
            endpoint = "/agents"
            logger.debug(f"Creating new agent with name: {agent.name}")
            response = self.client.post(endpoint, json=agent.dict())
            response.raise_for_status()
            agent_out = AgentOut.parse_obj(response.json())
            logger.info(f"Agent created with id: {agent_out.id}")
            return agent_out
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while creating agent: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while creating agent: {str(e)}")
            raise

    def get_agent(self, agent_id: str) -> AgentOut:
        """
        Retrieve details of a specific agent.

        Args:
            agent_id (str): The unique identifier of the agent.

        Returns:
            AgentOut: The agent data.

        Raises:
            httpx.HTTPError: If the HTTP request fails.
        """
        try:
            endpoint = f"/agents/{agent_id}"
            logger.debug(f"Retrieving agent with id: {agent_id}")
            response = self.client.get(endpoint)
            response.raise_for_status()
            agent_out = AgentOut.parse_obj(response.json())
            logger.info(f"Retrieved agent: {agent_out.name} (id: {agent_out.id})")
            return agent_out
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while getting agent {agent_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while getting agent {agent_id}: {str(e)}")
            raise

    def update_agent(self, agent_id: str, update: AgentUpdate) -> AgentOut:
        """
        Update an existing agent.

        Args:
            agent_id (str): The unique identifier of the agent.
            update (AgentUpdate): The update data.

        Returns:
            AgentOut: The updated agent data.

        Raises:
            httpx.HTTPError: If the HTTP request fails.
        """
        try:
            endpoint = f"/agents/{agent_id}"
            logger.debug(
                f"Updating agent with id: {agent_id} with data: {update.dict(exclude_unset=True)}"
            )
            response = self.client.put(endpoint, json=update.dict(exclude_unset=True))
            response.raise_for_status()
            agent_out = AgentOut.parse_obj(response.json())
            logger.info(f"Updated agent: {agent_out.name} (id: {agent_out.id})")
            return agent_out
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while updating agent {agent_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while updating agent {agent_id}: {str(e)}")
            raise

    def execute_agent(
        self, agent_id: str, payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute an agent manually.

        Args:
            agent_id (str): The unique identifier of the agent.
            payload (Optional[Dict[str, Any]], optional): The execution payload. Defaults to None.

        Returns:
            Dict[str, Any]: The response from the execution endpoint.

        Raises:
            httpx.HTTPError: If the HTTP request fails.
        """
        try:
            endpoint = f"/agents/{agent_id}/execute"
            payload_obj = ExecutionPayload(payload=payload or {})
            logger.debug(
                f"Executing agent with id: {agent_id} with payload: {payload_obj.payload}"
            )
            response = self.client.post(endpoint, json=payload_obj.dict())
            response.raise_for_status()
            result = response.json()
            logger.info(f"Executed agent {agent_id}. Response: {result}")
            return result
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while executing agent {agent_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while executing agent {agent_id}: {str(e)}")
            raise

    def get_agent_history(self, agent_id: str) -> AgentExecutionHistory:
        """
        Fetch the execution history (logs) for an agent.

        Args:
            agent_id (str): The unique identifier of the agent.

        Returns:
            AgentExecutionHistory: The agent's execution logs.

        Raises:
            httpx.HTTPError: If the HTTP request fails.
        """
        try:
            endpoint = f"/agents/{agent_id}/history"
            logger.debug(f"Fetching execution history for agent id: {agent_id}")
            response = self.client.get(endpoint)
            response.raise_for_status()
            history = AgentExecutionHistory.parse_obj(response.json())
            logger.info(f"Retrieved execution history for agent id: {agent_id}")
            return history
        except httpx.HTTPError as e:
            logger.error(
                f"HTTP error while getting history for agent {agent_id}: {str(e)}"
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error while getting history for agent {agent_id}: {str(e)}"
            )
            raise

    def batch_execute_agents(
        self, agents: List[AgentOut], payload: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """
        Batch execute multiple agents.

        Args:
            agents (List[AgentOut]): The list of agents to execute.
            payload (Optional[Dict[str, Any]], optional): The execution payload to use for all agents.
                Defaults to None.

        Returns:
            List[Any]: A list containing the response for each agent execution.

        Raises:
            httpx.HTTPError: If the HTTP request fails.
        """
        try:
            endpoint = "/agents/batch_execute"
            payload_obj = ExecutionPayload(payload=payload or {})
            agents_list = [agent.dict() for agent in agents]
            logger.debug(
                f"Batch executing {len(agents)} agents with payload: {payload_obj.payload}"
            )
            response = self.client.post(
                endpoint, json={"agents": agents_list, **payload_obj.dict()}
            )
            response.raise_for_status()
            results = response.json()
            logger.info(f"Batch executed {len(agents)} agents.")
            return results
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during batch execution: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during batch execution: {str(e)}")
            raise

    def health(self) -> Dict[str, Any]:
        """
        Check the health of the API.

        Returns:
            Dict[str, Any]: The health status.

        Raises:
            httpx.HTTPError: If the HTTP request fails.
        """
        try:
            endpoint = "/health"
            logger.debug("Checking API health.")
            response = self.client.get(endpoint)
            response.raise_for_status()
            status_info = response.json()
            logger.info(f"API health: {status_info}")
            return status_info
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while checking health: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while checking health: {str(e)}")
            raise

    # Context manager support for use in 'with' statements.
    def __enter__(self) -> "SwarmCloudAPI":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


# ------------------------------------------------------------------------------
# Example Usage (can be removed or commented out in production)
# ------------------------------------------------------------------------------

# if __name__ == "__main__":
#     # Example: Using the client in a script
#     try:
#         client = SwarmCloudAPI(api_key="your_api_key_here")
#         logger.info("Checking API health...")
#         print(client.health())

#         logger.info("Listing agents...")
#         agents = client.list_agents()
#         for agent in agents:
#             print(agent)

#         # Example: Creating a new agent
#         new_agent_data = AgentCreate(
#             name="ExampleAgent",
#             description="A sample agent for demonstration.",
#             code="def main(request, store):\n    return 'Hello, world!'",
#             requirements="",
#             envs="",
#             autoscaling=False,
#         )
#         created_agent = client.create_agent(new_agent_data)
#         print(f"Created agent: {created_agent}")

#     except httpx.HTTPError as http_err:
#         logger.error(f"HTTP error occurred: {http_err}")
#     except Exception as err:
#         logger.error(f"An unexpected error occurred: {err}")
#     finally:
#         client.close()
