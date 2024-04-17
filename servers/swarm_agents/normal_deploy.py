from dotenv import load_dotenv
import os

import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sse_starlette.sse import EventSourceResponse

from swarms_cloud.schema.cog_vlm_schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatMessageResponse,
    ModelCard,
    ModelList,
    UsageInfo,
)

# from exa.structs.parallelize_models_gpus import prepare_model_for_ddp_inference

# Load environment variables from .env file
load_dotenv()

# Environment variables
MODEL_PATH = os.environ.get("COGVLM_MODEL_PATH", "THUDM/cogvlm-chat-hf")
TOKENIZER_PATH = os.environ.get("TOKENIZER_PATH", "lmsys/vicuna-7b-v1.5")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
QUANT_ENABLED = os.environ.get("QUANT_ENABLED", True)

# Create a FastAPI app
app = FastAPI(
    title="Swarms Cloud API",
    description="A simple API server for Swarms Cloud",
    debug=True,
    version="1.0",
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
async def list_models():
    """
    An endpoint to list available models. It returns a list of model cards.
    This is useful for clients to query and understand what models are available for use.
    """
    model_card = ModelCard(
        id="cogvlm-chat-17b"
    )  # can be replaced by your model id like cogagent-chat-18b
    return ModelList(data=[model_card])


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    request: ChatCompletionRequest,  # token: str = Depends(authenticate_user)
):
    try:
        if len(request.messages) < 1 or request.messages[-1].role == "assistant":
            raise HTTPException(status_code=400, detail="Invalid request")

        # print(f"Request: {request}")
        dict(
            messages=request.messages,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens or 1024,
            echo=False,
            stream=request.stream,
        )

        if request.stream:
            # generate = predict(request.model, gen_params)
            generate = None
            return EventSourceResponse(generate, media_type="text/event-stream")

        # Generate response
        # response = generate_cogvlm(model, tokenizer, gen_params)
        response = None

        usage = UsageInfo()

        # ChatMessageResponse
        message = ChatMessageResponse(
            role="assistant",
            content=response["text"],
        )

        # # # Log the entry to supabase
        # entry = ModelAPILogEntry(
        #     user_id=fetch_api_key_info(token),
        #     model_id="41a2869c-5f8d-403f-83bb-1f06c56bad47",
        #     input_tokens=count_tokens(request.messages, tokenizer, request.model),
        #     output_tokens=count_tokens(response["text"], tokenizer, request.model),
        #     all_cost=calculate_pricing(
        #         texts=[message.content], tokenizer=tokenizer, rate_per_million=15.0
        #     ),
        #     input_cost=calculate_pricing(
        #         texts=[message.content], tokenizer=tokenizer, rate_per_million=15.0
        #     ),
        #     output_cost=calculate_pricing(
        #         texts=response["text"], tokenizer=tokenizer, rate_per_million=15.0
        #     )
        #     * 5,
        #     messages=request.messages,
        #     # temperature=request.temperature,
        #     top_p=request.top_p,
        #     # echo=request.echo,
        #     stream=request.stream,
        #     repetition_penalty=request.repetition_penalty,
        #     max_tokens=request.max_tokens,
        # )

        # # Log the entry to supabase
        # log_to_supabase(entry=entry)

        # ChatCompletionResponseChoice
        logger.debug(f"==== message ====\n{message}")
        choice_data = ChatCompletionResponseChoice(
            index=0,
            message=message,
        )

        # task_usage = UsageInfo.model_validate(response["usage"])
        task_usage = UsageInfo.parse_obj(response["usage"])
        for usage_key, usage_value in task_usage.dict().items():
            setattr(usage, usage_key, getattr(usage, usage_key) + usage_value)

        out = ChatCompletionResponse(
            model=request.model,
            choices=[choice_data],
            object="chat.completion",
            usage=usage,
        )

        return out
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("SWARM_AGENT_API_PORT", 8000)),
        log_level="info",
        use_colors=True,
    )
