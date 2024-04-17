from fastapi import Header, HTTPException
from typing_extensions import Annotated


async def verify_token(x_token: Annotated[str, Header()]) -> None:
    """Verify the token is valid."""
    # Replace this with your actual authentication logic
    if x_token != "secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")
