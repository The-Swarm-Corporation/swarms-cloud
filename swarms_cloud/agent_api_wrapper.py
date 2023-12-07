from fastapi import FastAPI, HTTPException
from typing import Callable, List, Type
from swarms.agents import Agent
import logging
from functools import wraps
import time


def expose_as_api(
    agent_class: Type[Agent],
    app: FastAPI,
    path: str,
    http_method: str = "get"
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
    >>> @expose_as_api(Agent, app, "/agent")
    ... def agent_method():
    ...     return "Hello World"
    
    """
    def decorator(func: Callable):
        async def endpoint_wrapper(*args, **kwargs):
            try:
                agent_instance = agent_class(*args, **kwargs)
                result = getattr(agent_instance, func.__name__)()
                return result
            except Exception as error:
                raise HTTPException(status_code=500, detail=str(error))
        if http_method.lower() == "get":
            app.get(path)(endpoint_wrapper)
        elif http_method.lower() == "post":
            app.post(path)(endpoint_wrapper)
        return func
    return decorator