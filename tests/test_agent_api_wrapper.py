import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from swarms.structs.agent import Agent
from swarms_cloud.main import agent_api_wrapper


@pytest.fixture
def app():
    return FastAPI()


@pytest.fixture
def client(app):
    return TestClient(app)


def test_get_endpoint_registration(app):
    @agent_api_wrapper(Agent, app, path="/test-get", http_method="get")
    def dummy_method():
        pass

    assert "/test-get" in [
        route.path for route in app.routes if route.methods == {"GET"}
    ]


def test_post_endpoint_registration(app):
    @agent_api_wrapper(Agent, app, path="/test-post", http_method="post")
    def dummy_method():
        pass

    assert "/test-post" in [
        route.path for route in app.routes if route.methods == {"POST"}
    ]


def test_agent_instantiation_with_args(app, monkeypatch):
    test_args = ("arg1", "arg2")

    def mock_init(self, *args, **kwargs):
        assert args == test_args

    monkeypatch.setattr(Agent, "__init__", mock_init)

    @agent_api_wrapper(Agent, app, path="/test-args", http_method="get")
    def dummy_method():
        pass

    client(app).get("/test-args", params={"args": test_args})


def test_successful_method_execution(app, monkeypatch):
    def mock_method(self):
        return "success"

    monkeypatch.setattr(Agent, "dummy_method", mock_method)

    @agent_api_wrapper(Agent, app, path="/test-success", http_method="get")
    def dummy_method():
        pass

    response = client(app).get("/test-success")
    assert response.text == "success"


def test_http_exception_on_failure(app, monkeypatch):
    def mock_method(self):
        raise ValueError("error")

    monkeypatch.setattr(Agent, "dummy_method", mock_method)

    @agent_api_wrapper(Agent, app, path="/test-exception", http_method="get")
    def dummy_method():
        pass

    response = client(app).get("/test-exception")
    assert response.status_code == 500
    assert "error" in response.text
