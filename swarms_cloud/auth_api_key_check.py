import requests
import os


def call_swarms_auth_api(
    url: str = "https://swarms.world/api/guard/auth",
    model_id: str = None,
    secret_key: str = None,
    organization_id: str = None,
    access_token: str = None,
    payload: dict = None,
) -> dict:
    """
    Sends a POST request to the given URL with the necessary headers and JSON payload.

    Args:
        url (str): The URL of the API endpoint.
        model_id (str): The model identifier to be included in the JSON payload.

    Returns:
        dict: The response from the API in JSON format, or an error message.
    """

    # Define headers
    headers = {
        "SecretKey": secret_key,  # Retrieves the secret key from environment variables
        "Swarms-Organization": organization_id,  # Optionally include your organization ID
        "Authorization": f"Bearer {access_token}",  # Authorization token, replace with actual token
    }

    # Check if the ModelID is present and valid
    payload = {"model": model_id}

    # Check if the SecretKey is present and valid
    if not headers["SecretKey"]:
        return {"message": "Secret Key is missing", "status": 401}
    if headers["SecretKey"] != os.getenv("GUARD_SECRET_KEY"):
        return {"message": "Invalid Secret Key", "status": 401}

    # Send POST request
    response = requests.post(url, headers=headers, json=payload)

    # Check the status of the response
    if response.status_code == 200:
        return response.json()  # Return the JSON response if the request was successful
    else:
        return {"message": "Failed to authenticate", "status": response.status_code}
