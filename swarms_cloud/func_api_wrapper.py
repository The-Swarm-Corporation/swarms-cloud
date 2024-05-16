import inspect
from typing import Callable, TypeVar, get_type_hints
import time
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import create_model
from typing import Any, Union, List
from swarms.structs.omni_agent_types import AgentType
from swarms.utils.loguru_logger import logger
from swarms.structs import BaseSwarm
from swarms_cloud.schema.openai_protocol import ModelCard, ModelList


try:
    from fastapi import APIRouter, Depends, FastAPI, Request, Response
except ImportError:
    # [server] extra not installed
    APIRouter = Depends = FastAPI = Request = Response = Any


# Genertic type for return type
T = TypeVar("T")


# Function API Wrapper for functions: [CLASS]
class SwarmCloud(BaseSwarm):
    """Functional API Wrapper"""

    def __init__(
        self,
        app: Union[FastAPI, APIRouter] = None,
        host: str = "0.0.0.0",
        models: List[AgentType] = None,
        port: int = 8000,
        local_api: bool = False,
        model_registry: ModelList = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.app = app
        self.host = host
        self.models = models
        self.port = port
        self.local_api = local_api
        self.error_handlers = {}

    def add_model_to_registry(self, model_name: str, *args, **kwargs):
        log = ModelCard(id=model_name, created=time.time(), *args, **kwargs)
        logger.info(f"Adding model {model_name} to registry")
        self.model_registry.data.append(log)
        logger.info("Model added")
        return log

    def get_model_registry(self):
        return self.model_registry

    def add(self, path: str, method: str = "post", *args, **kwargs):
        """Add an endpoint to the API

        Args:
            path (str): path to add the endpoint to (e.g. "/endpoint")
            method (str, optional): post . Defaults to "post".
        """

        def decorator(func: Callable):
            try:
                if method.lower() == "get":
                    endpoint_func = self.app.get(path)
                elif method.lower() == "post":
                    endpoint_func = self.app.post(path)
                elif method.lower == "put":
                    endpoint_func = self.app.put(path)
                elif method.lower == "delete":
                    endpoint_func = self.app.delete(path)
                elif method.lower == "patch":
                    endpoint_func = self.app.patch(path)

                else:
                    raise ValueError(f"Invalid method: {method}")

                @endpoint_func
                async def endpoint_wrapper(*args, **kwargs):
                    try:
                        logger.info(f"Calling method {func.__name__}")
                        result = func(*args, **kwargs)
                        return result
                    except Exception as error:
                        logger.error(f"Error in {func.__name__}: {error}")
                        raise HTTPException(status_code=500, detail=str(error))

                # Register the endpoint with the http method
                endpoint_func = getattr(self.app, method.lower())
                endpoint_func(path)(endpoint_wrapper)
                return func
            except Exception as error:
                logger.info(f"Error in {func.__name__}: {error}")

        return decorator

    def run(self, *args, **kwargs):
        """Run the API"""
        try:
            uvicorn.run(self.app, host=self.host, port=self.port)
        except Exception as error:
            logger.error(f"Error in {self.__class__.__name__}: {error}")

    def __call__(self, *args, **kwargs):
        """Call the run method

        Args:

        """
        try:
            self.run(*args, **kwargs)
        except Exception as error:
            logger.error(f"Error in {self.__class__.__name__}: {error}")

    def add_endpoints(self, endpoints: list):
        """
        Batch addition of multiple endpoints.

        Args:
            endpoints (list): A list of tuples, each containing path, method, and function.
                              Example: [("/path1", "get", function1), ("/path2", "post", function2)]

        """
        for path, method, func in endpoints:
            self.add(path, method)(func)

    def _generate_request_model(self, func: Callable):
        """Generate requests model

        Args:
            func (Callable): function to generate the request model for

        Returns:
            : dynamically generated request model
        """
        # Extract arguments from the function signature
        signature = inspect.signature(func)
        fields = {
            name: (param.annotation, ...)
            for name, param in signature.parameters.items()
        }
        return create_model(f"{func.__name__}Request", **fields)

    def _generate_response_model(self, func: Callable):
        """Generate response model

        Args:
            func (Callable): function to generate the response model for

        Returns:
            : dynamically generated response model
        """
        return_type = get_type_hints(func).get("return")
        return create_model(f"{func.__name__}Response", result=(return_type, ...))

    def add_error_handler(
        self, exception_class: type, handler: Callable[[Request, Exception], Response]
    ):
        """Add an error handler

        Args:
            exception_class (type): exception class to handle
            handler (Callable[[Request, Exception], Response]): handler function
        """
        self.error_handlers[exception_class] = handler

    async def _call_async_func(self, func, **kwargs):
        """Call an async function

        Args:
            func (callable): function to call

        """
        if inspect.iscoroutinefunction(func):
            return await func(**kwargs)
        else:
            return func(**kwargs)
