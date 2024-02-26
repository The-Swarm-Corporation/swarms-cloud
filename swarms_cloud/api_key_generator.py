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
