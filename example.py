import os

from dotenv import load_dotenv

# Import the OpenAIChat model and the Agent struct
from swarms.models import OpenAIChat
from swarms.structs import Agent
from swarms_cloud import FuncAPIWrapper

api = FuncAPIWrapper()

# Load the environment variables
load_dotenv()

# Get the API key from the environment
api_key = os.environ.get("OPENAI_API_KEY")

# Initialize the language model
llm = OpenAIChat(
    temperature=0.5,
    model_name="gpt-4",
    openai_api_key=api_key,
)


@api.add("/agent1", method="post")
def agent(task: str):
    ## Initialize the workflow
    agent = Agent(
        llm=llm,
        max_loops=1,
        autosave=True,
        dashboard=True,
    )

    # Run the workflow on a task
    out = agent.run(task)
    print(out)
