import os

from dotenv import load_dotenv

# Import the OpenAIChat model and the Agent struct
from swarms.models import OpenAIChat
from swarms.structs import Agent

from swarms_cloud.func_api_wrapper import FuncAPIWrapper

# Load the environment variables
load_dotenv()

# Get the API key from the environment
api_key = os.environ.get("OPENAI_API_KEY")


# Initialize the API wrapper
api = FuncAPIWrapper(
    port=8001,
)


# Initialize the language model
llm = OpenAIChat(
    temperature=0.5,
    model_name="gpt-4",
    openai_api_key=api_key,
)


## Initialize the workflow
agent = Agent(
    llm=llm,
    max_loops=1,
    autosave=True,
    dashboard=True,
)


@api.add("/agent", method="post")
def agent_method(task: str):
    """Agent method

    Args:
        task (str): Task to perform

    Returns:
        str: Response from the agent
    """
    try:
        out = agent.run(task=task)
        return {"status": "success", "task": task, "response": out}
    except Exception as error:
        return {"status": "error", "task": task, "response": str(error)}


# Run the API
api.run()
