import secrets
import string


def generate_api_key(prefix: str = "sk-", length: int = 50, *args, **kwargs):
    """Generate a random api key

    Args:
        prefix (str, optional): Prefix. Defaults to "sk-".
        length (int, optional): length of the apikey. Defaults to 50.

    Raises:
        ValueError: _description_
        RuntimeError: _description_

    Returns:
        _type_: _description_


    Example:
    >>> from swarms_cloud.api_key_generator import generate_api_key
    >>> generate_api_key()
    >>> sk-9a7b8c5d6e7f8g9h0i1j2k3l4m5n6o7p8q9r0s1t2u3v4w5x6y7z8A9B0C1D2E3F4G5H6I7J8K9L0M1N2O3P4Q5R6S7T8U9V0W1X2Y3Z4
    """
    if length <= len(prefix):
        raise ValueError("Length must be greater than prefix length")

    try:
        # Generate a random string of letters for the api
        characters = string.ascii_letters + string.digits
        secure_key = "".join(secrets.choice(characters) for _ in range(length))
        return prefix + secure_key
    except Exception as error:
        # Handle unexpeccted errors
        raise RuntimeError(f"Error generating api key: {error}")
