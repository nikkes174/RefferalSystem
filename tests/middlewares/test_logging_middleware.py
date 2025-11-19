import json
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware

from backend.middlewares.logging import LoggingMiddleware


class FakeCorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request.state.correlation_id = "test-corr-id"
        return await call_next(request)


def create_app():
    app = FastAPI()

    app.add_middleware(FakeCorrelationIdMiddleware)
    app.add_middleware(LoggingMiddleware)

    @app.get("/hello")
    async def hello():
        return {"msg": "world"}

    return app


def test_logging_middleware_prints_log():
    app = create_app()
    client = TestClient(app)

    with patch("builtins.print") as mock_print:
        response = client.get("/hello")

    assert response.status_code == 200
    assert response.json() == {"msg": "world"}

    mock_print.assert_called_once()

    log_str = mock_print.call_args[0][0]
    log_data = json.loads(log_str)

    assert log_data["correlation_id"] == "test-corr-id"
    assert log_data["method"] == "GET"
    assert log_data["path"] == "/hello"
    assert log_data["status"] == 200

    assert isinstance(log_data["duration"], float)
    assert log_data["duration"] >= 0
