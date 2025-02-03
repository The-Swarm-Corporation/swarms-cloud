import requests
import json
import time

# Configuration
BASE_URL = "https://swarmcloud-285321057562.us-central1.run.app"
API_KEY = "sk-5701eba12a7716137d10ad1e3064cdb449f468d8d4375d00b3e1b0cdcefc7b59"  # Replace with your actual API key
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}


def print_response(title: str, response_data: dict):
    print(f"\n=== {title} ===")
    print(json.dumps(response_data, indent=2, sort_keys=True))


def test_health():
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print_response("Health check response", response.json())
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root():
    print("\n=== Testing Root Endpoint ===")
    response = requests.get(f"{BASE_URL}/")
    print_response("Root endpoint response", response.json())
    assert response.status_code == 200
    assert "status" in response.json()


def test_create_agent():
    print("\n=== Testing Create Agent ===")
    agent_data = {
        "name": "TestAgent",
        "description": "A test agent",
        "code": """def main(request, store):
    return "Hello from test agent!"
""",
        "requirements": "requests==2.28.1",
        "envs": "DEBUG=True",
        "autoscaling": True,
    }

    response = requests.post(f"{BASE_URL}/agents", headers=HEADERS, json=agent_data)
    print_response("Create agent response", response.json())
    assert response.status_code == 201
    return response.json()["id"]


def test_list_agents():
    print("\n=== Testing List Agents ===")
    response = requests.get(f"{BASE_URL}/agents", headers=HEADERS)
    print_response("List agents response", response.json())
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_agent(agent_id):
    print("\n=== Testing Get Agent ===")
    response = requests.get(f"{BASE_URL}/agents/{agent_id}", headers=HEADERS)
    print_response("Get agent response", response.json())
    assert response.status_code == 200
    assert response.json()["id"] == agent_id


def test_update_agent(agent_id):
    print("\n=== Testing Update Agent ===")
    update_data = {"name": "UpdatedTestAgent", "description": "An updated test agent"}
    response = requests.put(
        f"{BASE_URL}/agents/{agent_id}", headers=HEADERS, json=update_data
    )
    print_response("Update agent response", response.json())
    assert response.status_code == 200
    assert response.json()["name"] == "UpdatedTestAgent"


def test_execute_agent(agent_id):
    print("\n=== Testing Execute Agent ===")
    payload = {"payload": {"test": "data"}}
    response = requests.post(
        f"{BASE_URL}/agents/{agent_id}/execute", headers=HEADERS, json=payload
    )
    print_response("Execute agent response", response.json())
    assert response.status_code == 200
    assert "return_value" in response.json()


def test_get_agent_history(agent_id):
    print("\n=== Testing Get Agent History ===")
    response = requests.get(f"{BASE_URL}/agents/{agent_id}/history", headers=HEADERS)
    print_response("Get agent history response", response.json())
    assert response.status_code == 200
    assert "executions" in response.json()


def test_delete_agent(agent_id):
    print("\n=== Testing Delete Agent ===")
    response = requests.delete(f"{BASE_URL}/agents/{agent_id}", headers=HEADERS)
    try:
        print_response("Delete agent response", response.json())
    except:
        print(f"Delete agent status code: {response.status_code}")
    assert response.status_code == 204


def run_all_tests():
    try:
        # Test basic endpoints
        test_health()
        test_root()

        # Test agent lifecycle
        agent_id = test_create_agent()
        time.sleep(1)  # Small delay to ensure agent is created

        test_list_agents()
        test_get_agent(agent_id)
        test_update_agent(agent_id)
        test_execute_agent(agent_id)
        test_get_agent_history(agent_id)
        test_delete_agent(agent_id)

        print("\n=== All tests completed successfully! ===")
    except AssertionError as e:
        error_data = {"error": "AssertionError", "message": str(e)}
        print("\n❌ Test failed:")
        print(json.dumps(error_data, indent=2))
    except Exception as e:
        error_data = {"error": e.__class__.__name__, "message": str(e)}
        print("\n❌ Error during tests:")
        print(json.dumps(error_data, indent=2))


if __name__ == "__main__":
    run_all_tests()
