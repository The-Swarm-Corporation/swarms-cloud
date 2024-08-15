from http import HTTPStatus

from fastapi.responses import JSONResponse

from swarms_cloud.schema.openai_protocol import (  # noqa: E501
    ErrorResponse,
)


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
