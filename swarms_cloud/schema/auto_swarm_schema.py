import uuid
from pydantic import BaseModel
from typing import Optional, Sequence, Dict, List

swarm_id = uuid.uuid4()


class AutoSwarmSchemaResponse(BaseModel):
    """
    Represents the schema for an auto swarm.

    Attributes:
        id (str): The ID of the swarm.
        api_key (Optional[str]): The API key for the swarm.
        swarm_name (Optional[str]): The name of the swarm.
        num_of_agents (Optional[int]): The number of agents in the swarm.
        messages (Optional[Dict[str, str]]): The messages for the swarm.
        num_loops (Optional[int]): The number of loops for the swarm.
        streaming (Optional[bool]): Indicates if the swarm is streaming.
        tasks (Optional[Sequence[str]]): The tasks for the swarm.
        max_tokens (Optional[int]): The maximum number of tokens for the swarm.
        documents (Optional[Sequence[str]]): The documents for the swarm.
        response_format (Optional[str]): The response format for the swarm.
        stopping_token (Optional[List[str]]): The stopping tokens for the swarm.
        number_of_choices (Optional[int]): The number of choices for the swarm.
    """

    id: str = str(swarm_id)
    api_key: Optional[str] = None
    swarm_name: Optional[str] = None
    num_of_agents: Optional[int] = None
    messages: Optional[Dict[str, str]] = None
    num_loops: Optional[int] = 1
    streaming: Optional[bool] = False
    tasks: Optional[Sequence[str]] = None
    max_tokens: Optional[int] = 32096
    documents: Optional[Sequence[str]] = None
    response_format: Optional[str] = None
    stopping_token: Optional[List[str]] = []
    n: Optional[int] = 1


class AutoSwarmResponse(BaseModel):
    """
    Represents the response for an auto swarm.

    Attributes:
        id (str): The ID of the auto swarm.
        swarm_name (Optional[str]): The name of the auto swarm (optional).
        num_of_agents (Optional[int]): The number of agents in the auto swarm (optional).
        messages (Optional[Dict[str, str]]): Additional messages related to the auto swarm (optional).
        num_loops (Optional[int]): The number of loops to run the auto swarm (optional, default: 1).
        streaming (Optional[bool]): Indicates if the auto swarm should be streamed (optional, default: False).
        tasks (Optional[Sequence[str]]): The tasks to be performed by the auto swarm (optional).
        max_tokens (Optional[int]): The maximum number of tokens to generate for each task (optional).
        response_format (Optional[str]): The format of the response (optional).
        stopping_token (Optional[List[str]]): The stopping token(s) for each task (optional).
        number_of_choices (Optional[int]): The number of choices to generate for each task (optional, default: 1).
    """

    id: str
    swarm_name: Optional[str] = None
    num_of_agents: Optional[int] = None
    messages: Optional[Dict[str, str]] = None
    num_loops: Optional[int] = 1
    streaming: Optional[bool] = False
    tasks: Optional[Sequence[str]] = None
    max_tokens: Optional[int] = None
    response_format: Optional[str] = None
    stopping_token: Optional[List[str]] = None
    number_of_choices: Optional[int] = 1
