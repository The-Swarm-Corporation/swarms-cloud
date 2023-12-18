from pydantic import BaseModel
from typing import Optional, List, Any, Callable


class AgentParameters(BaseModel):
    """Agent Parameters

    Args:
    temperature (float, optional): _description_. Defaults to None.
    model_name (str, optional): _description_. Defaults to None.
    openai_api_key (str, optional): _description_. Defaults to None.
    id (str, optional): _description_. Defaults to None.
    llm (Any, optional): _description_. Defaults to None.
    template (Optional[str], optional): _description_. Defaults to None.
    max_loops (int, optional): _description_. Defaults to 5.
    stopping_condition (Optional[Callable], optional): _description_. Defaults to None.
    loop_interval (int, optional): _description_. Defaults to 1.
    retry_attempts (int, optional): _description_. Defaults to 3.
    retry_interval (int, optional): _description_. Defaults to 1.
    return_history (bool, optional): _description_. Defaults to False.
    stopping_token (str, optional): _description_. Defaults to None.
    dynamic_loops (Optional[bool], optional): _description_. Defaults to False.
    interactive (bool, optional): _description_. Defaults to False.
    dashboard (bool, optional): _description_. Defaults to False.
    agent_name (str, optional): _description_. Defaults to "Autonomous-Agent-XYZ1B".
    agent_description (str, optional): _description_. Defaults to None.
    system_prompt (str, optional): _description_. Defaults to None.
    tools (List[Any], optional): _description_. Defaults to None.
    dynamic_temperature_enabled (Optional[bool], optional): _description_. Defaults to False.
    sop (Optional[str], optional): _description_. Defaults to None.
    sop_list (Optional[List[str]], optional): _description_. Defaults to None.
    saved_state_path (Optional[str], optional): _description_. Defaults to None.
    autosave (Optional[bool], optional): _description_. Defaults to False.
    context_length (Optional[int], optional): _description_. Defaults to 8192.
    user_name (str, optional): _description_. Defaults to "Human:".
    self_healing_enabled (Optional[bool], optional): _description_. Defaults to False.
    code_interpreter (Optional[bool], optional): _description_. Defaults to False.
    multi_modal (Optional[bool], optional): _description_. Defaults to None.
    pdf_path (Optional[str], optional): _description_. Defaults to None.


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
