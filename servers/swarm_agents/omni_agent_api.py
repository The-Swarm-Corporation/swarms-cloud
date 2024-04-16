from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.runnables import RunnableLambda
from langserve import add_routes
from swarms import Anthropic
from swarms.agents.omni_modal_agent import OmniModalAgent


def agent_run_task(task: str):
    # Agent
    agent = OmniModalAgent(
        llm=Anthropic(),
        verbose=True,
    )

    return agent.run(task)


agent = RunnableLambda(agent_run_task)

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
    # dependencies=[Depends()],
)


# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

add_routes(
    app,
    agent,
    path="/v1/chat/completions",
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
