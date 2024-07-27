import asyncio
import os
from typing import List
import uvicorn
import tiktoken
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from swarms import Agent, Anthropic, GPT4o, GPT4VisionAPI, OpenAIChat
from swarms.utils.loguru_logger import logger
from swarms_cloud.schema.cog_vlm_schemas import ChatCompletionResponse, UsageInfo

# Define the input model using Pydantic
class AgentInput(BaseModel):
    agent_name: str = "Swarm Agent"
    system_prompt: str = None
    agent_description: str = None
    model_name: str = "OpenAIChat"
    max_loops: int = 1
    autosave: bool = False
    dynamic_temperature_enabled: bool = False
    dashboard: bool = False
    verbose: bool = False
    streaming_on: bool = True
    saved_state_path: str = None
    sop: str = None
    sop_list: List[str] = None
    user_name: str = "User"
    retry_attempts: int = 3
    context_length: int = 8192
    task: str = None

# Define the output model using Pydantic
class AgentOutput(BaseModel):
    agent: AgentInput
    completions: ChatCompletionResponse

# Define the available models
AVAILABLE_MODELS = ["OpenAIChat", "GPT4o", "GPT4VisionAPI", "Anthropic"]

def count_tokens(text: str):
    try:
        # Get the encoding for the specific model
        encoding = tiktoken.get_encoding("gpt-4o")

        # Encode the text
        tokens = encoding.encode(text)

        # Count the tokens
        token_count = len(tokens)

        return token_count
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

llm = OpenAIChat()
def model_router(model_name: str):
    """
    Function to switch to the specified model.

    Parameters:
    - model_name (str): The name of the model to switch to.

    Returns:
    - None

    Raises:
    - None

    """
    # Logic to switch to the specified model
    if model_name == "OpenAIChat":
        # Switch to OpenAIChat model
        llm = OpenAIChat()
    elif model_name == "GPT4o":
        # Switch to GPT4o model
        llm = GPT4o(openai_api_key=os.getenv("OPENAI_API_KEY"))
    elif model_name == "GPT4VisionAPI":
        # Switch to GPT4VisionAPI model
        llm = GPT4VisionAPI()
    elif model_name == "Anthropic":
        # Switch to Anthropic model
        llm = Anthropic(anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"))
    else:
        # Invalid model name
        raise HTTPException(status_code=400, detail=f"Invalid model name: {model_name}")

    return llm

async def agent_completions(agent_input: AgentInput):
    #try:
    if True:
        logger.info(f"Received request: {agent_input}")
        llm = model_router(agent_input.model_name)

        agent = Agent(
            agent_name=agent_input.agent_name,
            system_prompt=agent_input.system_prompt,
            agent_description=agent_input.agent_description,
            llm=llm,
            max_loops=agent_input.max_loops,
            autosave=agent_input.autosave,
            dynamic_temperature_enabled=agent_input.dynamic_temperature_enabled,
            dashboard=agent_input.dashboard,
            verbose=agent_input.verbose,
            streaming_on=agent_input.streaming_on,
            saved_state_path=agent_input.saved_state_path,
            sop=agent_input.sop,
            sop_list=agent_input.sop_list,
            user_name=agent_input.user_name,
            retry_attempts=agent_input.retry_attempts,
            context_length=agent_input.context_length,
        )

        # Run the agent
        logger.info(f"Running agent with task: {agent_input.task}")
        
        completions = agent.run(agent_input.task)

        logger.info(f"Completions: {completions}")
        input_history = agent.short_memory.return_history_as_string()
        all_input_tokens = count_tokens(input_history)
        output_tokens = count_tokens(completions)

        logger.info(f"Token counts: {all_input_tokens}, {output_tokens}")

        out = AgentOutput(
            agent=agent_input,
            completions=ChatCompletionResponse(
                choices=[
                    {
                        "index": 0,
                        "message": {
                            "role": agent_input.agent_name,
                            "content": completions,
                            "name": None,
                        },
                    }
                ],
                stream_choices=None,
                usage_info=UsageInfo(
                    prompt_tokens=all_input_tokens,
                    completion_tokens=output_tokens,
                    total_tokens=all_input_tokens + output_tokens,
                ),
            ),
        )
        ret = out.json()
        print(f"RET {str(ret)}")
        return out.json()

    #except Exception as e:
    #    raise HTTPException(status_code=400, detail=str(e))

async def main():
    agent_input = AgentInput(model_name="OpenAIChat",
                             agent_name="plato",
                             system_prompt="you are a philosopher",
                             task="what is the meaning of life?")
    await agent_completions(agent_input)
    
if __name__ == "__main__":
    asyncio.run(main())
