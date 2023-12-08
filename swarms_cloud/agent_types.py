from pydantic import BaseModel
from typing import Optional, List, Any, Callable


class AgentParameters(BaseModel):
    """Agent Parameters

    Args:
        BaseModel (_type_): _description_
    """

    temperature: float = None
    model_name: str = None
    openai_api_key: str = None
    id: str = None
    llm: Any = None
    template: Optional[str] = None
    max_loops = 5
    stopping_condition: Optional[Callable] = None
    loop_interval: int = 1
    retry_attempts: int = 3
    retry_interval: int = 1
    return_history: bool = False
    stopping_token: str = None
    dynamic_loops: Optional[bool] = False
    interactive: bool = False
    dashboard: bool = False
    agent_name: str = "Autonomous-Agent-XYZ1B"
    agent_description: str = None
    system_prompt: str = None
    tools: List[Any] = None
    dynamic_temperature_enabled: Optional[bool] = False
    sop: Optional[str] = None
    sop_list: Optional[List[str]] = None
    saved_state_path: Optional[str] = None
    autosave: Optional[bool] = False
    context_length: Optional[int] = 8192
    user_name: str = "Human:"
    self_healing_enabled: Optional[bool] = False
    code_interpreter: Optional[bool] = False
    multi_modal: Optional[bool] = None
    pdf_path: Optional[str] = None
    list_of_pdf: Optional[str] = None
    tokenizer: Optional[Any] = None
    memory: Optional[Any] = None
    preset_stopping_token: Optional[bool] = False


class AgentInput(BaseModel):
    task: str
    img: str = None
    parameters: AgentParameters
