from http import HTTPStatus
from typing import Any, List, Optional

from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer

from swarms_cloud.schema.openai_protocol import (  # noqa: E501
    ErrorResponse,
)


class VariableInterface:
    """A IO interface maintaining variables."""

    async_engine: Any = None
    api_keys: Optional[List[str]] = None
    qos_engine: Any = None
    request_hosts = []


get_bearer_token = HTTPBearer(auto_error=False)


async def check_api_key(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
) -> str:
    """Check if client provide valid api key.

    Adopted from https://github.com/lm-sys/FastChat/blob/v0.2.35/fastchat/serve/openai_api_server.py#L108-L127
    """  # noqa
    if VariableInterface.api_keys:
        if (
            auth is None
            or (token := auth.credentials) not in VariableInterface.api_keys
        ):
            raise HTTPException(
                status_code=401,
                detail={
                    "error": {
                        "message": "Please request with valid api key!",
                        "type": "invalid_request_error",
                        "param": None,
                        "code": "invalid_api_key",
                    }
                },
            )
        return token
    else:
        # api_keys not set; allow all
        return None


def get_model_list():
    """Available models."""
    # Use the model registry from swarms
    return [
        "Qwen/Qwen-VL-Chat-Int4",
        "Qwen/Qwen-VL-Chat",
        "Qwen/Qwen-VL",
    ]


def create_error_response(status: HTTPStatus, message: str):
    """Create error response according to http status and message.

    Args:
        status (HTTPStatus): HTTP status codes and reason phrases
        message (str): error message
    """
    return JSONResponse(
        ErrorResponse(
            message=message, type="invalid_request_error", code=status.value
        ).model_dump()
    )


async def check_request(request) -> Optional[JSONResponse]:
    """Check if a request is valid."""
    if request.model in get_model_list():
        return
    ret = create_error_response(
        HTTPStatus.NOT_FOUND, f"The model `{request.model}` does not exist."
    )
    return ret
