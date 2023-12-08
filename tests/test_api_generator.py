from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, HTTPException
from swarms.structs.agent import Agent

from swarms_cloud.api_key_generator import generate_api_key
from swarms_cloud.main import agent_api_wrapper


# Basic tests
def test_generate_api_key_default():
    api_key = generate_api_key()
    assert isinstance(api_key, str)
    assert api_key.startswith("sk-")
    assert len(api_key) == 52  # Prefix (3) + 50 random characters


def test_generate_api_key_custom_length():
    api_key = generate_api_key(length=10)
    assert len(api_key) == 13  # Prefix (3) + 10 random characters


def test_generate_api_key_custom_prefix():
    api_key = generate_api_key(prefix="custom-")
    assert api_key.startswith("custom-")
    assert len(api_key) == 57  # Custom prefix (7) + 50 random characters


# Exception tests
def test_generate_api_key_short_length():
    with pytest.raises(ValueError):
        generate_api_key(length=2)


def test_generate_api_key_unexpected_error():
    with pytest.raises(RuntimeError):
        generate_api_key(length=1000000)


# Parameterized tests
@pytest.mark.parametrize(
    "prefix, length",
    [
        ("pre-", 15),
        ("test-", 25),
        ("longprefix-", 100),
    ],
)
def test_generate_api_key_parameterized(prefix, length):
    api_key = generate_api_key(prefix=prefix, length=length)
    assert api_key.startswith(prefix)
    assert len(api_key) == len(prefix) + length


# Test performance (optional)
def test_generate_api_key_performance(benchmark):
    benchmark(generate_api_key)


# Additional tests
def test_generate_api_key_invalid_prefix_type():
    with pytest.raises(ValueError):
        generate_api_key(prefix=123)


def test_generate_api_key_negative_length():
    with pytest.raises(ValueError):
        generate_api_key(length=-10)


def test_generate_api_key_empty_prefix():
    api_key = generate_api_key(prefix="")
    assert api_key.startswith("sk-")
    assert len(api_key) == 53  # Prefix (3) + 50 random characters


def test_generate_api_key_special_characters_prefix():
    api_key = generate_api_key(prefix="@#$")
    assert api_key.startswith("@#$")
    assert len(api_key) == 53  # Special prefix (3) + 50 random characters


def test_generate_api_key_prefix_length():
    api_key = generate_api_key(prefix="x" * 100)
    assert len(api_key) == 150  # Custom prefix (100) + 50 random characters


def test_generate_api_key_zero_length():
    with pytest.raises(ValueError):
        generate_api_key(length=0)


def test_generate_api_key_zero_length_custom_prefix():
    with pytest.raises(ValueError):
        generate_api_key(prefix="custom-", length=0)


def test_generate_api_key_negative_length_custom_prefix():
    with pytest.raises(ValueError):
        generate_api_key(prefix="custom-", length=-10)


def test_generate_api_key_long_prefix():
    api_key = generate_api_key(prefix="verylongprefix-")
    assert api_key.startswith("verylongprefix-")
    assert len(api_key) == 63  # Custom prefix (16) + 50 random characters


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
    MockAgent()
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
    MockAgent()
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
