import logging
from typing import Callable

import uvicorn
from fastapi import FastAPI, HTTPException

# Logger initialization
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Function API Wrapper for functions: [CLASS]
class FuncAPIWrapper:
    """Functional API Wrapper


    Args:
        host (str, optional): Host to run the API on. Defaults to "
        port (int, optional): Port to run the API on. Defaults to 8000.

    Methods:
        add: Add an endpoint to the API
        run: Run the API

    Example:
    >>> api = FuncAPIWrapper()
    >>> @api.add("/endpoint")
    ... def endpoint():
    ...     return "Hello World"
    >>> api.run()


    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8000,
        local_api: bool = False,
        *args,
        **kwargs,
    ):
        self.host = host
        self.port = port
        self.app = FastAPI()

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
