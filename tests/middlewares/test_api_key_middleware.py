import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.database.base import Base
from backend.ExternalService.models import ExternalService
from main import app


@pytest.fixture
async def session():
    """in-memory тестовая БД."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    # создаём таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as s:
        yield s


@pytest.fixture
def client():
    """Тестовый клиент FastAPI с подключённым middleware."""
    return TestClient(app)


async def create_service(session):
    """Создание внешнего сервиса для тестирования API key."""
    svc = ExternalService(
        id=uuid.uuid4(),
        service_name="test_svc",
        api_key="SECRET-KEY-123",
        webhook_url=None,
        created_at=datetime.utcnow(),
    )
    session.add(svc)
    await session.flush()
    return svc


@pytest.mark.asyncio
async def test_open_paths_allowed_without_api_key(client):
    """Open paths должны работать без API key."""
    r1 = client.get("/docs")
    r2 = client.get("/openapi.json")
    r3 = client.get("/health")

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r3.status_code in (200, 404)


@pytest.mark.asyncio
async def test_missing_api_key_blocked(client):
    """Если ключ не передали — 401."""
    response = client.get("/referrals/some/uuid")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing API key"


@pytest.mark.asyncio
async def test_invalid_api_key_blocked(client):
    """Неверный ключ → 403."""
    response = client.get(
        "/referrals/some/uuid",
        headers={"X-API-Key": "WRONG-KEY"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid API key"


@pytest.mark.asyncio
async def test_valid_api_key_passes(session, client, monkeypatch):
    """Корректный API key должен пропускать запрос."""

    svc = await create_service(session)

    async def fake_get_session():
        yield session

    # --- Главный фикс ---
    # Патчим глобальное db.get_session, чтобы middleware использовал session из фикстуры
    monkeypatch.setattr("backend.middlewares.api_key.db.get_session", lambda: fake_get_session())

    # Выполняем запрос
    response = client.get(
        f"/referrals/top/{svc.id}",
        headers={"X-API-Key": svc.api_key}
    )
    print("BODY:", response.text)
    print("STATUS:", response.status_code)

    # Middleware должен пропустить запрос → ожидаем 200 или 404
    assert response.status_code in (200, 404)
