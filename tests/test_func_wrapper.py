import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from swarms_cloud import FuncAPIWrapper, api_wrapper


# Create an instance of FuncAPIWrapper for testing
@pytest.fixture
def api():
    return FuncAPIWrapper()


# Create a test client
@pytest.fixture
def client(api):
    return TestClient(api.app)


# Define some sample functions to test
def sample_function():
    return "Hello World"


def sample_function_with_error():
    raise Exception("Test Error")


# Define tests for FuncAPIWrapper
def test_api_wrapper_decorator(api):
    @api.add("/endpoint")
    def endpoint():
        return "Hello World"

    assert api.app.routes[-1].path == "/endpoint"
    assert api.app.routes[-1].endpoint.__name__ == "endpoint"


def test_func_api_wrapper_run(api, client):
    @api.add("/endpoint")
    def endpoint():
        return "Hello World"

    response = client.get("/endpoint")
    assert response.status_code == 200
    assert response.text == "Hello World"


def test_func_api_wrapper_error_handling(api, client):
    @api.add("/endpoint")
    def endpoint():
        raise Exception("Test Error")

    response = client.get("/endpoint")
    assert response.status_code == 500


# Define tests for api_wrapper decorator
def test_api_wrapper_success(client):
    app = FuncAPIWrapper()

    @api_wrapper(app.app, "/endpoint")
    def endpoint():
        return "Hello World"

    response = client.get("/endpoint")
    assert response.status_code == 200
    assert response.text == "Hello World"


def test_api_wrapper_error_handling(client):
    app = FuncAPIWrapper()

    @api_wrapper(app.app, "/endpoint")
    def endpoint():
        raise Exception("Test Error")

    response = client.get("/endpoint")
    assert response.status_code == 500


# Add more tests as needed

# ...
