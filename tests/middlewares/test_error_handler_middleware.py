from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware

from backend.middlewares.errors import ErrorHandlerMiddleware


class FakeCorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.correlation_id = "test-corr-id"
        return await call_next(request)


def create_app():
    app = FastAPI()

    app.add_middleware(FakeCorrelationMiddleware)
    app.add_middleware(ErrorHandlerMiddleware)

    @app.get("/ok")
    async def ok():
        return {"status": "ok"}

    @app.get("/value-error")
    async def raise_value_error():
        raise ValueError("Invalid data example")

    @app.get("/exception")
    async def raise_exception():
        raise RuntimeError("Unexpected failure")

    return app


app = create_app()
client = TestClient(app)


def test_ok_response_not_modified():
    """Проверяем, что успешный запрос не меняется middleware'ом."""
    response = client.get("/ok")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_value_error_handled():
    """ValueError → 400 + корректный JSON + correlation_id."""
    response = client.get("/value-error")

    assert response.status_code == 400

    data = response.json()
    assert data["status"] == "error"
    assert data["detail"] == "Invalid data example"
    assert data["correlation_id"] == "test-corr-id"


def test_unexpected_exception_handled():
    """Любой Exception → 500 + Internal server error + correlation_id."""
    response = client.get("/exception")

    assert response.status_code == 500

    data = response.json()
    assert data["status"] == "error"
    assert data["detail"] == "Internal server error"
    assert data["correlation_id"] == "test-corr-id"
