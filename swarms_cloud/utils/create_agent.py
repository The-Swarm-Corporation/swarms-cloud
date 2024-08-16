import asyncio
import os

from pydantic import ValidationError
from swarms import Agent, OpenAIChat

from swarms_cloud.schema.agent_api_schemas import AgentInput


def create_agent_sync(input_data: AgentInput) -> Agent:
    """
    Creates an agent based on the provided input data synchronously.

    Args:
        input_data (AgentInput): The input data model for the agent configuration.

    Returns:
        Agent: The configured agent ready to run.

    Raises:
        ValueError: If validation fails for the input data.
    """
    try:
        # Validate input data
        input_data.validate(input_data.dict())

        # Initialize the model
        model = OpenAIChat(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name=input_data.model_name,
            temperature=0.1,
        )

        # Initialize and return the agent
        agent = Agent(
            agent_name=input_data.agent_name,
            system_prompt=input_data.system_prompt,
            llm=model,
            max_loops=input_data.max_loops,
            dynamic_temperature_enabled=input_data.dynamic_temperature_enabled,
            streaming_on=input_data.streaming_on,
            sop=input_data.sop,
            sop_list=input_data.sop_list,
            user_name=input_data.user_name,
            retry_attempts=input_data.retry_attempts,
            context_length=input_data.context_length,
            max_tokens=input_data.max_tokens,
            tool_schema=input_data.tool_schema,
            # long_term_memory=input_data.long_term_memory,
            # tools=input_data.tools,
        )
        return agent

    except ValidationError as e:
        print(f"Validation Error: {e}")
        raise


async def create_agent_async(input_data: AgentInput) -> Agent:
    """
    Creates an agent based on the provided input data asynchronously.

    Args:
        input_data (AgentInput): The input data model for the agent configuration.

    Returns:
        Agent: The configured agent ready to run.

    Raises:
        ValueError: If validation fails for the input data.
    """
    try:
        # Validate input data
        input_data.validate(input_data.dict())

        # Simulate async operation, e.g., fetching API keys
        await asyncio.sleep(0)  # Replace with actual async operation if needed

        # Initialize the model
        model = OpenAIChat(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name=input_data.model_name,
            temperature=0.1,
        )

        # Initialize and return the agent
        agent = Agent(
            agent_name=input_data.agent_name,
            system_prompt=input_data.system_prompt,
            llm=model,
            max_loops=input_data.max_loops,
            dynamic_temperature_enabled=input_data.dynamic_temperature_enabled,
            streaming_on=input_data.streaming_on,
            sop=input_data.sop,
            sop_list=input_data.sop_list,
            user_name=input_data.user_name,
            retry_attempts=input_data.retry_attempts,
            context_length=input_data.context_length,
            max_tokens=input_data.max_tokens,
            tool_schema=input_data.tool_schema,
            # long_term_memory=input_data.long_term_memory,
            # tools=input_data.tools,
        )
        return agent

    except ValidationError as e:
        print(f"Validation Error: {e}")
        raise
