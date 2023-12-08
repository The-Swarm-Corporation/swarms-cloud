import logging
from typing import Callable, Type, Optional

from fastapi import FastAPI, HTTPException
from swarms.structs.agent import Agent

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def agent_api_wrapper(
    agent_class: Type[Agent],
    app: FastAPI,
    path: Optional[str] = None,
    http_method: Optional[str] = "get",
    logging: bool = False,
    *args,
    **kwargs,
):
    """Expose agent methods as API endpoints

    Args:
        agent_class (Type[Agent]): _description_
        app (FastAPI): _description_
        path (str): _description_
        http_method (str, optional): _description_. Defaults to "get".

    Example:
    >>> from swarms.agents import Agent
    >>> from fastapi import FastAPI
    >>> app = FastAPI()
    >>> @agent_api_wrapper(Agent, app, "/agent")
    ... def agent_method():
    ...     return "Hello World"

    """

    def decorator(func: Callable):
        async def endpoint_wrapper(*args, **kwargs):
            try:
                logger.info(
                    f"Creating instance of {agent_class.__name__} with args: {args} and kwargs: {kwargs}"
                )
                agent_instance = agent_class(*args, **kwargs)
                logger.info(f"Calling method {func.__name__} of {agent_class.__name__}")
                result = getattr(agent_instance, func.__name__)()
                logger.info(
                    f"Method {func.__name__} of {agent_class.__name__} returned: {result}"
                )
                return result
            except Exception as error:
                logger.error(f"An error occurred: {str(error)}")
                raise HTTPException(status_code=500, detail=str(error))

        if http_method.lower() == "get":
            logger.info(f"Registering GET endpoint at {path}")
            app.get(path)(endpoint_wrapper)
        elif http_method.lower() == "post":
            logger.info(f"Registering POST endpoint at {path}")
            app.post(path)(endpoint_wrapper)
        return func

    return decorator
