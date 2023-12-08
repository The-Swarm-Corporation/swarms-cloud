import pytest
from unittest.mock import MagicMock

from fastapi import FastAPI, HTTPException
from swarms.structs.agent import Agent

from swarms_cloud.main import agent_api_wrapper


class MockAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.method_called = False

    def mock_method(self):
        self.method_called = True
        return "Hello World"


@pytest.mark.parametrize(
    "http_method",
    ["get", "post"],
)
def test_decorator_registers_endpoint(http_method):
    # Arrange
    app = FastAPI()
    path = "/agent"

    # Act
    @agent_api_wrapper(MockAgent, app, path, http_method=http_method)
    def mock_method():
        return "Hello World"

    # Assert
    if http_method == "get":
        assert "GET" in app.routes
    else:
        assert "POST" in app.routes

    assert path in app.routes


def test_decorator_logs_correctly():
    # Arrange
    app = FastAPI()
    path = "/agent"
    logger = MagicMock()

    # Act
    @agent_api_wrapper(MockAgent, app, path, logging=True)
    def mock_method():
        return "Hello World"

    # Assert
    assert logger.info.call_count == 3
    assert logger.error.call_count == 0


def test_endpoint_wrapper_calls_agent_method():
    # Arrange
    app = FastAPI()
    path = "/agent"
    agent_instance = MockAgent()

    # Act
    @agent_api_wrapper(MockAgent, app, path)
    def mock_method():
        return "Hello World"

    # Assert
    assert agent_instance.mock_method.called


def test_endpoint_wrapper_returns_result():
    # Arrange
    app = FastAPI()
    path = "/agent"
    agent_instance = MockAgent()
    expected_result = "Hello World"

    # Act
    @agent_api_wrapper(MockAgent, app, path)
    def mock_method():
        return expected_result

    # Assert
    response = app.get(path)
    assert response.status_code == 200
    assert response.json() == expected_result


def test_endpoint_wrapper_raises_exception():
    # Arrange
    app = FastAPI()
    path = "/agent"
    agent_instance = MockAgent()
    expected_error = Exception("Test error")

    # Act
    @agent_api_wrapper(MockAgent, app, path)
    def mock_method():
        raise expected_error

    # Assert
    with pytest.raises(HTTPException) as error:
        app.get(path)

    assert error.value.status_code == 500
    assert error.value.detail == str(expected_error)
