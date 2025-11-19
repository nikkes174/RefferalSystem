import uuid

import pytest

from backend.ExternalService.models import ExternalService
from backend.ExternalService.repository import ExternalServiceRepository


@pytest.mark.asyncio
async def test_create_service(session):
    repo = ExternalServiceRepository()

    service = ExternalService(
        id=uuid.uuid4(),
        service_name="test_service",
        api_key="secret123",
        webhook_url="https://example.com/hook",
    )

    created = await repo.create_service(session, service)

    assert created.id == service.id
    assert created.service_name == "test_service"

    saved = await session.get(ExternalService, created.id)
    assert saved is not None


@pytest.mark.asyncio
async def test_get_by_api_key(session):
    repo = ExternalServiceRepository()

    service = ExternalService(
        id=uuid.uuid4(),
        service_name="abc",
        api_key="my-key",
        webhook_url=None,
    )
    session.add(service)
    await session.flush()

    found = await repo.get_by_api_key(session, "my-key")

    assert found is not None
    assert found.service_name == "abc"


@pytest.mark.asyncio
async def test_get_by_api_key_not_found(session):
    repo = ExternalServiceRepository()

    found = await repo.get_by_api_key(session, "no-such-key")

    assert found is None


@pytest.mark.asyncio
async def test_update_webhook(session):
    repo = ExternalServiceRepository()

    service = ExternalService(
        id=uuid.uuid4(),
        service_name="hello",
        api_key="123",
        webhook_url=None,
    )
    session.add(service)
    await session.flush()

    updated = await repo.update_webhook(
        session,
        service_id=service.id,
        webhook_url="https://new-url.com",
    )

    assert updated is not None
    assert updated.webhook_url == "https://new-url.com"


@pytest.mark.asyncio
async def test_get_by_id(session):
    repo = ExternalServiceRepository()

    service = ExternalService(
        id=uuid.uuid4(),
        service_name="getme",
        api_key="xx",
        webhook_url=None,
    )
    session.add(service)
    await session.flush()

    found = await repo.get_by_id(session, service.id)

    assert found is not None
    assert found.id == service.id
