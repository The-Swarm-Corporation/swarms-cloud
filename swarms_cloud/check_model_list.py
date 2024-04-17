from http import HTTPStatus
from typing import Optional

from fastapi.responses import JSONResponse

from swarms_cloud.schema.openai_protocol import (  # noqa: E501
    ErrorResponse,
)


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
