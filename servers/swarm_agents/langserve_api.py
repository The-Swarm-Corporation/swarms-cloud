import subprocess

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.runnables import RunnableLambda
from langserve import add_routes
from swarms import Agent, Anthropic, tool


# Model
llm = Anthropic(
    temperature=0.1,
)


# Tools
@tool
def terminal(
    code: str,
):
    """
    Run code in the terminal.

    Args:
        code (str): The code to run in the terminal.

    Returns:
        str: The output of the code.
    """
    out = subprocess.run(code, shell=True, capture_output=True, text=True).stdout
    return str(out)


@tool
def browser(query: str):
    """
    Search the query in the browser with the `browser` tool.

    Args:
        query (str): The query to search in the browser.

    Returns:
        str: The search results.
    """
    import webbrowser

    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return f"Searching for {query} in the browser."


@tool
def create_file(file_path: str, content: str):
    """
    Create a file using the file editor tool.

    Args:
        file_path (str): The path to the file.
        content (str): The content to write to the file.

    Returns:
        str: The result of the file creation operation.
    """
    with open(file_path, "w") as file:
        file.write(content)
    return f"File {file_path} created successfully."


@tool
def file_editor(file_path: str, mode: str, content: str):
    """
    Edit a file using the file editor tool.

    Args:
        file_path (str): The path to the file.
        mode (str): The mode to open the file in.
        content (str): The content to write to the file.

    Returns:
        str: The result of the file editing operation.
    """
    with open(file_path, mode) as file:
        file.write(content)
    return f"File {file_path} edited successfully."


def agent_run_task(task: str) -> str:
    # Agent
    agent = Agent(
        agent_name="Devin",
        system_prompt=(
            "Autonomous agent that can interact with humans and other"
            " agents. Be Helpful and Kind. Use the tools provided to"
            " assist the user. Return all code in markdown format."
        ),
        llm=llm,
        max_loops=1,
        autosave=True,
        dashboard=False,
        streaming_on=True,
        verbose=True,
        stopping_token="<DONE>",
        tools=[terminal, browser, file_editor, create_file],
    )

    return agent.run(task)


agent = RunnableLambda(agent_run_task)

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
    dependencies=[Depends()],
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
    path="/test",
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
