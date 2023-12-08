from fastapi import FastAPI
from swarms_cloud.main import agent_api_wrapper
from pydantic import BaseModel
from swarms.structs import Agent
from swarms.models import OpenAIChat


class AgentParameters(BaseModel):
    temperature: float
    model_name: str
    openai_api_key: str
    max_loops: int
    autosave: bool
    dashboard: bool


class AgentInput(BaseModel):
    task: str
    parameters: AgentParameters


app = FastAPI()


@agent_api_wrapper(Agent, app, "/agent", http_method="post")
def run_agent(agent_input: AgentInput):
    agent_parameters = agent_input.parameters
    llm = OpenAIChat(
        temperature=agent_parameters.temperature,
        model_name=agent_parameters.model_name,
        openai_api_key=agent_parameters.openai_api_key,
    )
    agent = Agent(
        llm=llm,
        max_loops=agent_parameters.max_loops,
        autosave=agent_parameters.autosave,
        dashboard=agent_parameters.dashboard,
    )
    return agent.run(agent_input.task)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
