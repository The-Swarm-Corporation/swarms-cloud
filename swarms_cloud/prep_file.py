def wrap_file_with_fastapi(
    input_file_path, output_file_path, endpoint_path, http_method="post"
):
    # Read the input file
    with open(input_file_path, "r") as file:
        original_code = file.read()

    # Extract the main logic into a new function
    agent_function_logic = """
    def run_agent_task():
        # Original agent logic
        agent = Agent(
            llm=llm,
            max_loops=1,
            autosave=True,
            dashboard=True,
        )
        return agent.run("Generate a 10,000 word blog on health and wellness.")
        """

    # Full template with FastAPI and agent_api_wrapper
    fastapi_template = f"""import os
    from dotenv import load_dotenv
    from fastapi import FastAPI
    from swarms.models import OpenAIChat
    from swarms.structs import Agent
    from your_module_where_decorator_is import agent_api_wrapper

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

    app = FastAPI()

    @agent_api_wrapper(Agent, app, path="{endpoint_path}", http_method="{http_method}")
    {agent_function_logic}

    # Original code without the agent initialization and run logic
    {original_code}
    """

    # Remove the original Agent initialization and run logic from the original code
    fastapi_template = fastapi_template.replace("## Initialize the workflow\n", "")
    fastapi_template = fastapi_template.replace(
        "agent = Agent(\n    llm=llm,\n    max_loops=1,\n    autosave=True,\n    dashboard=True,\n)\n\n",
        "",
    )
    fastapi_template = fastapi_template.replace(
        '# Run the workflow on a task\nout = agent.run("Generate a 10,000 word blog on health and wellness.")\nprint(out)',
        "",
    )

    # Write the modified code to a new output file
    with open(output_file_path, "w") as file:
        file.write(fastapi_template)


# Example usage
wrap_file_with_fastapi("input_file.py", "output_file.py", "/run-agent")
