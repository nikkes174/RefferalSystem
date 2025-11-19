import uuid
from datetime import datetime

import pytest

from backend.ExternalService.models import ExternalService
from backend.ExternalService.repository import ExternalServiceRepository


@pytest.fixture
def repo():
    return ExternalServiceRepository()


async def create_service(session):
    svc = ExternalService(
        id=uuid.uuid4(),
        service_name="test-service",
        api_key="key123",
        webhook_url="https://example.com",
        created_at=datetime.utcnow(),
    )
    session.add(svc)
    await session.flush()
    return svc


@pytest.mark.asyncio
async def test_add_log(repo, async_session):
    svc = await create_service(async_session)

    log = await repo.add_log(
        async_session,
        service_id=svc.id,
        event_type="info",
        message="Test log entry",
    )

    assert log.id is not None
    assert log.service_id == svc.id
    assert log.event_type == "info"
    assert log.message == "Test log entry"


@pytest.mark.asyncio
async def test_get_logs(repo, async_session):
    svc = await create_service(async_session)

    await repo.add_log(async_session, svc.id, "info", "First")
    await repo.add_log(async_session, svc.id, "error", "Second")

    logs = await repo.get_logs(async_session, svc.id)

    assert len(logs) == 2


@pytest.mark.asyncio
async def test_get_logs_filtered(repo, async_session):
    svc = await create_service(async_session)

    await repo.add_log(async_session, svc.id, "info", "Log A")
    await repo.add_log(async_session, svc.id, "error", "Log B")

    logs = await repo.get_logs(async_session, svc.id, event_type="error")

    assert len(logs) == 1
    assert logs[0].event_type == "error"
