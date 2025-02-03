#!/usr/bin/env python
"""
A simple testing suite for the Swarm Deployment API.

This script performs the following operations:
  1. Create a new swarm (simulate uploading a Docker Hub URL).
  2. List all swarms for the current user.
  3. Retrieve a specific swarm by its ID.
  4. Update the swarm.
  5. Delete the swarm.

All operations are logged using Loguru.
"""

import time
import uuid
import requests
from loguru import logger

# Configuration
BASE_URL = "https://swarmcloud-285321057562.us-central1.run.app"  # Change if your API is running elsewhere.
TEST_API_KEY = "user-api-key-123"
HEADERS = {"x-api-key": TEST_API_KEY, "Content-Type": "application/json"}


def log_response(response: requests.Response) -> None:
    """
    Logs the HTTP response status code and body.
    """
    logger.info("Response Code: {}", response.status_code)
    try:
        logger.info("Response JSON: {}", response.json())
    except Exception:
        logger.info("Response Text: {}", response.text)


def test_create_swarm() -> str:
    """
    Tests the creation of a new swarm.
    
    Returns:
        str: The ID of the created swarm.
    """
    url = f"{BASE_URL}/swarms/"
    payload = {
        "name": f"TestSwarm-{uuid.uuid4()}",
        "description": "This is a test swarm created during integration testing.",
        "dockerhub_image": "langchain/langchain",
        "min_replicas": 1,
        "max_replicas": 3,
        "target_cpu": 60
    }
    logger.info("Creating a new swarm with payload: {}", payload)
    response = requests.post(url, json=payload, headers=HEADERS)
    print(response.json())
    log_response(response)
    if response.status_code != 201:
        raise Exception("Failed to create swarm")
    swarm_id = response.json()["id"]
    logger.success("Swarm created with ID: {}", swarm_id)
    return swarm_id


def test_list_swarms() -> None:
    """
    Tests listing all swarms for the current user.
    """
    url = f"{BASE_URL}/swarms/"
    logger.info("Listing all swarms for current user")
    response = requests.get(url, headers=HEADERS)
    log_response(response)
    if response.status_code != 200:
        raise Exception("Failed to list swarms")
    swarms = response.json()
    logger.success("Found {} swarms.", len(swarms))


def test_get_swarm(swarm_id: str) -> None:
    """
    Tests retrieving a specific swarm by ID.
    
    Args:
        swarm_id (str): The swarm ID to retrieve.
    """
    url = f"{BASE_URL}/swarms/{swarm_id}"
    logger.info("Getting swarm with ID: {}", swarm_id)
    response = requests.get(url, headers=HEADERS)
    log_response(response)
    if response.status_code != 200:
        raise Exception(f"Failed to get swarm with ID: {swarm_id}")
    logger.success("Swarm details retrieved for ID: {}", swarm_id)


def test_update_swarm(swarm_id: str) -> None:
    """
    Tests updating a swarm's description.
    
    Args:
        swarm_id (str): The swarm ID to update.
    """
    url = f"{BASE_URL}/swarms/{swarm_id}"
    update_payload = {
        "description": "Updated description for testing purposes.",
        "min_replicas": 2,
        "max_replicas": 4,
        "target_cpu": 70
    }
    logger.info("Updating swarm {} with payload: {}", swarm_id, update_payload)
    response = requests.put(url, json=update_payload, headers=HEADERS)
    log_response(response)
    if response.status_code != 200:
        raise Exception(f"Failed to update swarm with ID: {swarm_id}")
    logger.success("Swarm {} updated successfully.", swarm_id)


def test_delete_swarm(swarm_id: str) -> None:
    """
    Tests deletion of a swarm.
    
    Args:
        swarm_id (str): The swarm ID to delete.
    """
    url = f"{BASE_URL}/swarms/{swarm_id}"
    logger.info("Deleting swarm with ID: {}", swarm_id)
    response = requests.delete(url, headers=HEADERS)
    if response.status_code != 204:
        log_response(response)
        raise Exception(f"Failed to delete swarm with ID: {swarm_id}")
    logger.success("Swarm {} deleted successfully.", swarm_id)


def main() -> None:
    """
    Main test sequence execution.
    """
    logger.info("Starting API integration tests.")
    try:
        swarm_id = test_create_swarm()
        # Pause to let the deployment settle (if needed)
        time.sleep(3)
        test_list_swarms()
        test_get_swarm(swarm_id)
        test_update_swarm(swarm_id)
        # Pause a moment to ensure updates propagate
        time.sleep(2)
        test_delete_swarm(swarm_id)
        logger.success("All API tests completed successfully.")
    except Exception as e:
        logger.exception("Test failed: {}", e)


if __name__ == "__main__":
    main()
