import time
from typing import List, Any

from pydantic import BaseModel, model_validator

from swarms_cloud.schema.cog_vlm_schemas import ChatCompletionResponse



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
    streaming_on: bool = False
    saved_state_path: str = "agent_saved_state.json"
    sop: str = None
    sop_list: List[str] = None
    user_name: str = "User"
    retry_attempts: int = 3
    context_length: int = 8192
    task: str = None
    max_tokens: int = None
    tool_schema: Any = None

    @model_validator(mode="pre")
    def check_required_fields(cls, values):
        required_fields = [
            "agent_name",
            "system_prompt",
            "task",
            "max_loops",
            "context_window",
        ]

        for field in required_fields:
            if not values.get(field):

                raise ValueError(f"{field} must not be empty or null")

        if values["max_loops"] <= 0:
            raise ValueError("max_loops must be greater than 0")

        if values["context_window"] <= 0:
            raise ValueError("context_window must be greater than 0")

        return values


class ModelSchema(BaseModel):
    id: str = None
    object: str = "model"
    created_at: int = time.time()
    owned_by: str = "TGSC"


class ModelList(BaseModel):
    object: str = "list"
    data = List[ModelSchema] = []


# Define the output model using Pydantic
class GenerationMetrics(BaseModel):
    tokens_per_second: float = 0.0
    completion_time: float = 0.0


# Define the output model using Pydantic
class AgentOutput(BaseModel):
    agent: AgentInput
    completions: ChatCompletionResponse
    # metrics: GenerationMetrics

