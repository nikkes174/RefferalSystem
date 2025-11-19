import uuid

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_correlation_id_generated_if_missing():
    """Если клиент НЕ передал X-Correlation-Id — сервер должен создать новый UUID."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "X-Correlation-Id" in response.headers

    cid = response.headers["X-Correlation-Id"]
    uuid_obj = uuid.UUID(cid)
    assert str(uuid_obj) == cid


def test_correlation_id_preserved_if_present():
    """Если клиент передал X-Correlation-Id — сервер должен вернуть тот же."""
    custom_id = "test-correlation-123"

    response = client.get(
        "/openapi.json",
        headers={"X-Correlation-Id": custom_id},
    )

    assert response.status_code == 200
    assert response.headers["X-Correlation-Id"] == custom_id


def test_correlation_id_saved_in_request_state(monkeypatch):
    """Проверяем, что middleware сохраняет ID в request.state.correlation_id.
    Для этого временно создаём test endpoint.
    """
    captured_cid = None

    @app.get("/__test_state")
    def test_state(request):
        nonlocal captured_cid
        captured_cid = request.state.correlation_id
        return {"ok": True}

    response = client.get("/__test_state")

    assert response.status_code == 200
    assert captured_cid is not None

    assert response.headers["X-Correlation-Id"] == captured_cid
