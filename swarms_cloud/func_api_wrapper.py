import logging
from typing import Callable

import uvicorn
from fastapi import FastAPI, HTTPException

# Logger initialization
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Function API Wrapper for functions: [FUNCTION]
def api_wrapper(
    app: FastAPI,
    path: str,
    http_method: str = "post",
):
    """API Wrapper

    Args:
        app (FastAPI): _description_
        path (str): _description_
        http_method (str, optional): _description_. Defaults to "post".

    Example:
    >>> app = FastAPI()
    >>> @api_wrapper(app, "/endpoint")
    ... def endpoint():
    ...     return "Hello World"
    >>> uvicorn.run(app, host="")
    """

    def decorator(func: Callable):
        try:

            async def endpoint_wrapper(*args, **kwargs):
                try:
                    # Call the func with provided args
                    logger.info(f"Calling method {func.__name__}")
                    result = func(*args, **kwargs)
                    return result
                except Exception as error:
                    logger.error(f"Error in {func.__name__}: {error}")
                    raise HTTPException(status_code=500, detail=str(error))

            # Register the endpoint
            endpoint_func = getattr(app, http_method)
            endpoint_func(path)(endpoint_wrapper)
            return func
        except Exception as error:
            print(f"Error in {func.__name__}: {error}")

    return decorator


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

    def __init__(self, host: str = "0.0.0.0", port: int = 8000, *args, **kwargs):
        self.host = host
        self.port = port
        self.app = FastAPI()

    def add(self, path: str, method: str = "post", *args, **kwargs):
        """Add an endpoint to the API

        Args:
            path (str): _description_
            method (str, optional): _description_. Defaults to "post".
        """

        def decorator(func: Callable):
            try:
                if method.lower() == "get":
                    endpoint_func = self.app.get(path)
                elif method.lower() == "post":
                    endpoint_func = self.app.post(path)
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
        """Run the API

        Args:

        """
        uvicorn.run(self.app, host=self.host, port=self.port)

    def __call__(self, *args, **kwargs):
        """Call the run method

        Args:

        """
        self.run(*args, **kwargs)
