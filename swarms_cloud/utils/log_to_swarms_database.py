import requests


def log_agent_data(data_dict: dict, retry_attempts: int = 1) -> dict or None:
    """
    Logs agent data to the Swarms database with retry logic.

    Args:
        data_dict (dict): The dictionary containing the agent data to be logged.
        url (str): The URL of the Swarms database endpoint.
        headers (dict): The headers to be included in the request.
        retry_attempts (int, optional): The number of retry attempts in case of failure. Defaults to 3.

    Returns:
        dict or None: The JSON response from the server if successful, otherwise None.
    """
    url = "https://swarms.world/api/get-agents/log-agents"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-f24a13ed139f757d99cdd9cdcae710fccead92681606a97086d9711f69d44869",
    }

    # for attempt in range(retry_attempts):
    #     try:
    response = requests.post(url, json=data_dict, headers=headers)
    response.raise_for_status()
    response.json()
    # print(output)
    # except requests.exceptions.RequestException as e:
    #     logger.error("Error logging agent data (Attempt {}): {}", attempt + 1, e)
    # logger.error("Failed to log agent data after {} attempts.", retry_attempts)
    # return "success"
