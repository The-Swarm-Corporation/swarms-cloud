import ast
import astor


class CodeTransformer(ast.NodeTransformer):
    def __init__(self):
        self.agent_logic = []

    def visit_Assign(self, node):
        if (
            isinstance(node.value, ast.Call)
            and getattr(node.value.func, "id", "") == "Agent"
        ):
            self.agent_logic.append(node)
            return None
        return node

    def visit_Expr(self, node):
        if (
            isinstance(node.value, ast.Call)
            and getattr(node.value.func, "id", "") == "Agent"
        ):
            self.agent_logic.append(node)
            return None
        return node


def wrap_with_fastapi(input_code):
    tree = ast.parse(input_code)
    transformer = CodeTransformer()
    transformer.visit(tree)

    # Define the agent_method function
    agent_function = ast.FunctionDef(
        name="agent_method",
        args=ast.arguments(
            args=[],
            vararg=None,
            kwarg=None,
            posonlyargs=[],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        ),
        body=transformer.agent_logic,
        decorator_list=[
            ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="app", ctx=ast.Load()),
                    attr="post",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[ast.keyword(arg="path", value=ast.Str(s="/agent"))],
            )
        ],
    )

    # Add necessary imports
    imports = [
        ast.Import(names=[ast.alias(name="FastAPI", asname=None)]),
        ast.ImportFrom(
            module="swarms.structs.agent",
            names=[ast.alias(name="Agent", asname=None)],
            level=0,
        ),
        ast.ImportFrom(
            module="swarms_cloud",
            names=[ast.alias(name="agent_api_wrapper", asname=None)],
            level=0,
        ),
        ast.ImportFrom(
            module="uvicorn", names=[ast.alias(name="uvicorn", asname=None)], level=0
        ),
    ]

    # Insert imports at the beginning
    for imp in reversed(imports):
        tree.body.insert(0, imp)

    # Insert FastAPI app initialization
    tree.body.insert(
        len(imports),
        ast.Assign(
            targets=[ast.Name(id="app", ctx=ast.Store())],
            value=ast.Call(
                func=ast.Name(id="FastAPI", ctx=ast.Load()), args=[], keywords=[]
            ),
        ),
    )

    # Add the agent_method function
    tree.body.append(agent_function)

    # Code to run the app with uvicorn
    run_app_code = ast.parse(
        "if __name__ == '__main__':\n    uvicorn.run(app, host='0.0.0.0', port=8000)"
    ).body
    tree.body.extend(run_app_code)

    return astor.to_source(tree)


# Example Usage
input_code = """



import os

from dotenv import load_dotenv

# Import the OpenAIChat model and the Agent struct
from swarms.models import OpenAIChat
from swarms.structs import Agent

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


## Initialize the workflow
agent = Agent(
    llm=llm,
    max_loops=1,
    autosave=True,
    dashboard=True,
)

# Run the workflow on a task
out = agent.run("Generate a 10,000 word blog on health and wellness.")
print(out)



"""
output_code = wrap_with_fastapi(input_code)
print(output_code)
