import os
from typing import List

import tiktoken
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from swarms import Agent, Anthropic, GPT4VisionAPI, OpenAIChat
from swarms.utils.loguru_logger import logger
from swarms_cloud.schema.cog_vlm_schemas import ChatCompletionResponse, UsageInfo
from swarms_cloud.schema.agent_api_schemas import (
    AgentInput,
    AgentOutput,
    ModelList,
    ModelSchema,
)


async def count_tokens(text: str) -> int:
    try:
        # Get the encoding for the specific model
        enc = tiktoken.encoding_for_model("gpt-4o")

        # Encode the text
        tokens = enc.encode(text)

        # Count the tokens
        return len(tokens)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error counting tokens: {e}")


async def model_router(model_name: str):
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
    if model_name == "gpt-4o":
        # Switch to OpenAIChat model
        llm = OpenAIChat(max_tokens=4000, model_name="gpt-4o")
    elif model_name == "gpt-4-vision-preview":
        # Switch to GPT4VisionAPI model
        llm = GPT4VisionAPI(
            max_tokens=4000,
        )
    elif model_name == "Anthropic":
        # Switch to Anthropic model
        llm = Anthropic(anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"))
    else:
        # Invalid model name
        raise HTTPException(status_code=400, detail=f"Invalid model name: {model_name}")

    return llm


# Create a FastAPI app
app = FastAPI(
    debug=True,
    title="Swarm Agent API",
    version="0.1.0",
)

# Load the middleware to handle CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/v1/models", response_model=ModelList)
async def list_models() -> List[str]:
    """
    An endpoint to list available models. It returns a list of model names.
    This is useful for clients to query and understand what models are available for use.
    """
    models = ModelList(
        data=[
            ModelSchema(id="gpt-4o", created_at="OpenAI"),
            ModelSchema(id="gpt-4-vision-preview", created_at="OpenAI"),
            ModelSchema(id="Anthropic", created_at="Anthropic"),
            # ModelSchema(id="gpt-4o", created_at="OpenAI"),
            ## Llama3.1
        ]
    )

    return models


@app.post("/v1/agent/completions", response_model=AgentOutput)
async def agent_completions(agent_input: AgentInput):
    try:
        logger.info(f"Received request: {agent_input}")

        agent_name = agent_input.agent_name
        system_prompt = agent_input.system_prompt
        max_loops = agent_input.max_loops
        context_length = agent_input.context_length
        tools = agent_input.tool_schema
        task = agent_input.task

        # Model check
        model_name = agent_input.model_name
        model = await model_router(model_name)

        # Initialize the agent
        agent = Agent(
            agent_name=agent_name,
            system_prompt=system_prompt,
            agent_description=agent_input.agent_description,
            llm=model,
            max_loops=max_loops,
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
            context_length=context_length,
            tool_schema=tools,
        )

        # Run the agent
        logger.info(f"Running agent with task: {task}")
        agent_history = agent.short_memory.return_history_as_string()
        completions = agent.run(task)

        logger.info(f"Agent response: {completions}")

        # Costs calculation
        all_input_tokens = await count_tokens(agent_history)
        output_tokens = await count_tokens(completions)
        total_costs = all_input_tokens + output_tokens
        logger.info(f"Token counts: {total_costs}")

        # Prepare the output
        out = AgentOutput(
            agent=agent_input,
            completions=ChatCompletionResponse(
                model=model_name,
                object="chat.completion",
                choices=[
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": completions,
                            "name": agent_name,
                        },
                    }
                ],
                usage_info=UsageInfo(
                    prompt_tokens=all_input_tokens,
                    completion_tokens=output_tokens,
                    total_tokens=total_costs,
                ),
            ),
        )

        return out

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080, use_colors=True, log_level="info")
