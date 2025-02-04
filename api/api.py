#!/usr/bin/env python
"""
SwarmCloud Agent API (No Docker/Kubernetes)

This API allows users to create, update, delete, execute, and monitor Python agents.
An agent is defined by its name, description, Python script (with a main function),
requirements, and environment variables.

Agent executions are run directly in the host process using asynchronous background
threads to simulate auto scaling. In production, consider using a robust task queue or
worker pool that can dynamically scale (e.g., Celery, Dramatiq, or a serverless backend).

Endpoints include:
  - /agents                  [GET]    List all agents
  - /agents                  [POST]   Create a new agent
  - /agents/{agent_id}       [GET]    Get details of an agent
  - /agents/{agent_id}       [PUT]    Update an agent
  - /agents/{agent_id}       [DELETE] Delete an agent
  - /agents/{agent_id}/execute [POST] Execute an agent (manual run)
  - /agents/{agent_id}/history [GET]  Fetch execution history/logs

Requirements:
  - Python 3.8+
  - fastapi, uvicorn, pydantic, loguru, psutil
  - opentelemetry-sdk, opentelemetry-exporter-otlp, opentelemetry-instrumentation-fastapi


Date: 2025-02-03
"""

import asyncio
import os
import time
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

import psutil  # For memory usage
import supabase
from dotenv import load_dotenv
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Request,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# --- OpenTelemetry Setup ---
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pydantic import BaseModel, Field

load_dotenv()

# Setup tracing
resource = Resource(attributes={SERVICE_NAME: "Swarm-agent-api"})
tracer_provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(endpoint="localhost:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

# (Optional) Setup metrics if needed. See the opentelemetry metrics documentation.
# For brevity, this example focuses on tracing.
#
# --- End OpenTelemetry Setup ---

# --- Pydantic Models ---


def get_supabase_client():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    return supabase.create_client(supabase_url, supabase_key)


def check_api_key(api_key: str) -> bool:
    supabase_client = get_supabase_client()
    response = (
        supabase_client.table("swarms_cloud_api_keys")
        .select("*")
        .eq("key", api_key)
        .execute()
    )
    # Check if the response contains data and if the user exists
    print(response)
    return bool(response.data)


def get_user_id_from_api_key(api_key: str) -> str:
    """
    Maps an API key to its associated user ID.

    Args:
        api_key (str): The API key to look up

    Returns:
        str: The user ID associated with the API key

    Raises:
        ValueError: If the API key is invalid or not found
    """
    supabase_client = get_supabase_client()
    response = (
        supabase_client.table("swarms_cloud_api_keys")
        .select("user_id")
        .eq("key", api_key)
        .execute()
    )
    if not response.data:
        raise ValueError("Invalid API key")
    return response.data[0]["user_id"]


# global dictionary to store timestamps for each client IP
client_request_times = {}


def rate_limit_dependency(max_requests: int = 10, window_seconds: int = 60):
    """
    A dependency that enforces a simple rate limit.

    Args:
        max_requests (int): Maximum allowed requests within the window.
        window_seconds (int): The time window in seconds.

    Raises:
        HTTPException: If the client has exceeded the rate limit.
    """

    async def dependency(request: Request):
        # Get client IP address; if behind a proxy, adjust accordingly.
        client_ip = request.client.host

        # Get the current time
        now = time.time()

        # Get the list of previous request timestamps for this IP (or empty list)
        request_times = client_request_times.get(client_ip, [])

        # Remove timestamps that are outside the window
        request_times = [t for t in request_times if now - t < window_seconds]

        # Check if the client has exceeded the allowed number of requests
        if len(request_times) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests, please try again later.",
            )

        # Record the current request timestamp
        request_times.append(now)
        client_request_times[client_ip] = request_times


def verify_api_key(x_api_key: str = Header(...)) -> None:
    """
    Dependency to verify the API key.
    """
    if not check_api_key(x_api_key):
        raise HTTPException(status_code=403, detail="Invalid API Key")


def deduct_credits(api_key: str, amount: float, product_name: str) -> None:
    """
    Deduct a certain amount of credits for the given user and log the transaction.

    This function:
      1. Retrieves the user's current credits from the "swarms_cloud_users_credits" table.
      2. Verifies that the record exists and that the user has sufficient credits.
      3. Logs the intended transaction in the "swarms_cloud_services" table.
      4. Updates the user's credit balance by deducting the specified amount.

    Args:
        api_key (str): The API key used for the transaction.
        amount (float): The amount of credits to deduct.
        product_name (str): A description of the product or service for which credits are deducted.

    Raises:
        HTTPException: If the user's credit record is not found, if there are insufficient credits,
                       or if any database operation fails.
    """
    supabase_client = get_supabase_client()
    user_id = get_user_id_from_api_key(api_key)

    # --- 1. Fetch the user's current credit record ---
    response = (
        supabase_client.table("swarms_cloud_users_credits")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User credits record not found.",
        )

    user_record = response.data[0]
    current_credit = Decimal(user_record["credit"])
    deduction = Decimal(str(amount))  # Use Decimal for precise arithmetic

    # --- 2. Verify that sufficient credits are available ---
    if current_credit < deduction:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Insufficient credits."
        )

    # --- 3. Log the transaction in the swarms_cloud_services table first ---
    log_response = (
        supabase_client.table("swarms_cloud_services")
        .insert(
            {
                "user_id": user_id,
                "api_key": api_key,
                "charge_credit": int(
                    deduction
                ),  # Assuming credits are stored as integers
                "product_name": product_name,
            }
        )
        .execute()
    )

    if not log_response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log the credit transaction.",
        )

    # --- 4. Update the user's credit balance ---
    new_credit = current_credit - deduction

    update_response = (
        supabase_client.table("swarms_cloud_users_credits")
        .update({"credit": str(new_credit)})
        .eq("user_id", user_id)
        .execute()
    )

    if not update_response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update credits.",
        )


# Example usage within an endpoint:
#
# @app.post("/some-action")
# async def some_action(x_api_key: str = Header(...), some_payload: SomePayloadType):
#     # Verify API key and extract user_id (this depends on your authentication logic)
#     user_id = get_user_id_from_api_key(x_api_key)
#
#     # Deduct credits (e.g., 1 credit per action)
#     deduct_credits(user_id, 1)
#
#     # Proceed with the action
#     return {"detail": "Action completed, credit deducted."}


class AgentBase(BaseModel):
    name: str = Field(..., example="TranslateAgent")
    description: Optional[str] = Field(None, example="An agent that translates text")
    code: str = Field(
        ...,
        example=(
            "def main(request, store):\n"
            "    text = request.payload.get('text', '')\n"
            "    return f'You said: {text}'\n"
        ),
    )
    requirements: Optional[str] = Field(
        None,
        example="requests==2.25.1\nlangchain==0.3.11",
    )
    envs: Optional[str] = Field(
        None,
        example="DEBUG=True\nLOG_LEVEL=info",
    )


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
    envs: Optional[str] = None
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


# --- In-memory "databases" for agents and their execution histories ---

agents_db: Dict[str, AgentOut] = {}
executions_db: Dict[str, List[ExecutionLog]] = {}

# --- Helper Functions for Agent Execution ---


def record_execution(agent_id: str, log: str) -> None:
    """
    Record an execution log for the given agent.
    """
    execution = ExecutionLog(timestamp=datetime.utcnow(), log=log)
    executions_db.setdefault(agent_id, []).append(execution)
    logger.info(f"Recorded execution for agent {agent_id}: {log}")


def run_agent_code(agent: Any, payload: dict) -> Any:
    """
    Dynamically execute the agent's code.

    The agent code should define a main() function with one of these signatures:
      - def main(): ...
      - def main(request, store): ...
    A dummy request (with payload) and store are provided when necessary.
    """

    # Determine how to access the code: dictionary or Pydantic attribute.
    try:
        code_str = agent["code"] if isinstance(agent, dict) else agent.code
    except Exception as e:
        raise Exception(f"Error accessing agent code: {e}")

    local_env = {}
    try:
        exec(code_str, local_env)
    except Exception as e:
        raise Exception(f"Error compiling agent code: {e}")

    if "main" not in local_env:
        raise Exception("Agent code does not define a main() function")
    main_fn = local_env["main"]

    import inspect

    sig = inspect.signature(main_fn)
    try:
        if len(sig.parameters) == 0:
            result = main_fn()
        elif len(sig.parameters) == 2:
            # Create a proper dummy request instance.
            class DummyRequest:
                def __init__(self, payload):
                    self.scheduled = False
                    self.payload = payload

            request_obj = DummyRequest(payload)
            store = {}
            result = main_fn(request_obj, store)
        else:
            raise Exception(
                "main() function has an unsupported signature (expected 0 or 2 parameters)"
            )
    except Exception as e:
        raise Exception(f"Error executing agent main(): {e}")
    return result


async def execute_agent(agent: AgentOut, payload: dict) -> Any:
    """
    Execute the agent code asynchronously with OpenTelemetry instrumentation.
    This captures execution time and memory usage.
    """
    logger.info(f"Starting execution of agent {agent.id} with payload: {payload}")
    with tracer.start_as_current_span("execute_agent") as span:
        start_time = time.time()
        # Capture initial memory usage (in bytes)
        process = psutil.Process()
        mem_before = process.memory_info().rss
        try:
            # Run the agent code in a thread so as not to block the event loop.
            result = await asyncio.to_thread(run_agent_code, agent, payload)
            span.set_attribute("agent.execution.result", result)
        except Exception as e:
            span.record_exception(e)
            raise
        finally:
            end_time = time.time()
            mem_after = process.memory_info().rss
            execution_time = end_time - start_time
            mem_delta = mem_after - mem_before
            span.set_attribute("agent.execution.time", execution_time)
            span.set_attribute("agent.execution.memory_before", mem_before)
            span.set_attribute("agent.execution.memory_after", mem_after)
            span.set_attribute("agent.execution.memory_delta", mem_delta)
            log_msg = f"Execution succeeded with result: {result} (time: {execution_time:.4f}s, mem change: {mem_delta} bytes)"
            record_execution(agent.id, log_msg)
            logger.info(log_msg)
        return result


# --- FastAPI Application Setup ---

app = FastAPI(
    title="Swarm Agent API",
    description="API for managing and executing Python agents in the cloud without Docker/Kubernetes.",
    version="1.0.0",
)

# Instrument FastAPI with OpenTelemetry.
FastAPIInstrumentor.instrument_app(app)

# Enable CORS (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---


@app.get(
    "/agents",
    response_model=List[AgentOut],
    dependencies=[Depends(verify_api_key), Depends(rate_limit_dependency)],
)
async def list_agents() -> List[AgentOut]:
    """List all agents."""
    return list(agents_db.values())


@app.post(
    "/agents",
    response_model=AgentOut,
    status_code=201,
    dependencies=[Depends(verify_api_key), Depends(rate_limit_dependency)],
)
async def create_agent(agent_in: AgentCreate) -> AgentOut:
    """
    Create a new agent.

    The provided code is stored and will be executed directly when requested.
    """

    # deduct_credits(x_api_key, 0.1, "swarms_cloud_new_agent")

    agent_id = str(uuid.uuid4())
    agent = AgentOut(
        id=agent_id,
        name=agent_in.name,
        description=agent_in.description,
        code=agent_in.code,
        requirements=agent_in.requirements,
        envs=agent_in.envs,
        autoscaling=agent_in.autoscaling or False,
        created_at=datetime.utcnow(),
    )
    agents_db[agent_id] = agent
    record_execution(agent_id, "Agent created")
    logger.info(f"Created agent {agent_id}")
    return agent


@app.get(
    "/agents/{agent_id}",
    response_model=AgentOut,
    dependencies=[Depends(verify_api_key), Depends(rate_limit_dependency)],
)
async def get_agent(agent_id: str) -> AgentOut:
    """Retrieve details of a specific agent."""
    agent = agents_db.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@app.put(
    "/agents/{agent_id}",
    response_model=AgentOut,
    dependencies=[Depends(verify_api_key), Depends(rate_limit_dependency)],
)
async def update_agent(agent_id: str, agent_update: AgentUpdate) -> AgentOut:
    """
    Update an agent's information.

    For simplicity, updating an agent will affect future executions.
    """
    agent = agents_db.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    update_data = agent_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)
    agents_db[agent_id] = agent
    record_execution(agent_id, "Agent updated")
    logger.info(f"Updated agent {agent_id}")
    return agent


# @app.delete(
#     "/agents/{agent_id}", status_code=204, dependencies=[Depends(verify_api_key)]
# )
# async def delete_agent(agent_id: str) -> None:
#     """
#     Delete an agent.
#     """
#     agent = agents_db.pop(agent_id, None)
#     if not agent:
#         raise HTTPException(status_code=404, detail="Agent not found")
#     record_execution(agent_id, "Agent deleted")
#     executions_db.pop(agent_id, None)
#     logger.info(f"Deleted agent {agent_id}")


@app.post(
    "/agents/{agent_id}/execute",
    dependencies=[Depends(verify_api_key), Depends(rate_limit_dependency)],
)
async def execute_agent_endpoint(
    agent_id: str,
    exec_payload: ExecutionPayload,
    background_tasks: BackgroundTasks,
) -> Dict[str, Any]:
    """
    Execute an agent manually.

    The execution is performed asynchronously. If the agent was created with autoscaling enabled,
    multiple concurrent executions are allowed. Otherwise, the executions still run in the background.
    """
    # try:
    #     deduct_credits(x_api_key, 0.01, "swarms_cloud_execute_agent")
    # except Exception as e:
    #     raise HTTPException(status_code=402, detail=str(e))

    agent = agents_db.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    try:
        result = await execute_agent(agent, exec_payload.payload)
        return {"return_value": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/agents/{agent_id}/history",
    response_model=AgentExecutionHistory,
    dependencies=[Depends(verify_api_key), Depends(rate_limit_dependency)],
)
async def get_agent_history(agent_id: str) -> AgentExecutionHistory:
    """Fetch the execution history (logs) for an agent."""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    history = executions_db.get(agent_id, [])
    return AgentExecutionHistory(agent_id=agent_id, executions=history)


# Batch execute agents
@app.post(
    "/agents/batch_execute",
    dependencies=[Depends(verify_api_key), Depends(rate_limit_dependency)],
)
async def batch_execute_agents(
    agents: List[AgentOut], payload: ExecutionPayload
) -> List[Any]:
    # try:
    #     deduct_credits(x_api_key, 0.01 * len(agents), "swarms_cloud_batch_execute_agents")
    # except Exception as e:
    #     raise HTTPException(status_code=402, detail=str(e))

    """Batch execute agents."""
    results = await asyncio.gather(
        *[execute_agent(agent, payload.payload) for agent in agents]
    )
    return results


@app.get("/")
def root():
    return {"status": "Welcome to the SwarmCloud API"}


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Main Entrypoint ---

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
