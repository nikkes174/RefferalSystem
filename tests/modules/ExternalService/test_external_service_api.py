import uuid

import pytest
from httpx import AsyncClient

from backend.ExternalService.models import ExternalService


@pytest.mark.asyncio
async def test_register_external_service(app, client: AsyncClient):
    payload = {
        "service_name": "test-service",
        "webhook_url": "https://example.com/hook",
    }

    response = await client.post("/external-services/", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["service_name"] == "test-service"
    assert data["webhook_url"] == "https://example.com/hook"
    assert "api_key" in data


@pytest.mark.asyncio
async def test_update_webhook(app, client: AsyncClient, session):
    service = ExternalService(
        id=uuid.uuid4(),
        service_name="update-test",
        api_key="key123",
        webhook_url=None,
    )
    session.add(service)
    await session.flush()

    payload = {"webhook_url": "https://new-hook.com"}

    response = await client.patch(
        f"/external-services/{service.id}/webhook",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json()["webhook_url"] == "https://new-hook.com"


@pytest.mark.asyncio
async def test_update_webhook_not_found(app, client: AsyncClient):
    fake_id = uuid.uuid4()

    response = await client.patch(
        f"/external-services/{fake_id}/webhook",
        json={"webhook_url": "https://new.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Service not found"


@pytest.mark.asyncio
async def test_get_service_by_api_key(app, client: AsyncClient, session):
    service = ExternalService(
        id=uuid.uuid4(),
        service_name="lookup",
        api_key="find-me",
        webhook_url=None,
    )
    session.add(service)
    await session.flush()

    response = await client.get(
        "/external-services/by-api-key",
        params={"api_key": "find-me"},
    )

    assert response.status_code == 200
    assert response.json()["service_name"] == "lookup"


@pytest.mark.asyncio
async def test_get_service_by_api_key_not_found(app, client: AsyncClient):
    response = await client.get(
        "/external-services/by-api-key",
        params={"api_key": "xxx"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Invalid API key"


#
# NEW — правильные тесты архивирования
#


@pytest.mark.asyncio
async def test_archive_service_correct(app, client: AsyncClient, session):
    service = ExternalService(
        id=uuid.uuid4(),
        service_name="arch",
        api_key="arch123",
        webhook_url="https://old-hook.com",
    )
    session.add(service)
    await session.flush()

    response = await client.post(f"/external-services/{service.id}/archive")

    assert response.status_code == 200
    data = response.json()
    assert data["archived"] is True


@pytest.mark.asyncio
async def test_archive_service_not_found(app, client: AsyncClient):
    fake_id = uuid.uuid4()

    response = await client.post(f"/external-services/{fake_id}/archive")

    assert response.status_code == 404
    assert response.json()["detail"] == "Service not found"
