import uuid
from datetime import datetime

import pytest

from backend.ExternalService.models import ExternalService
from backend.ExternalService.repository import ExternalServiceRepository
from backend.ExternalService.services.webhook_logger import WebhookLogger


@pytest.fixture
def repo():
    return ExternalServiceRepository()


@pytest.fixture
def logger(repo):
    return WebhookLogger(repo)


async def create_service(session):
    svc = ExternalService(
        id=uuid.uuid4(),
        service_name="testsvc",
        api_key="abc123",
        webhook_url="https://example.com",
        created_at=datetime.utcnow(),
    )
    session.add(svc)
    await session.flush()
    return svc


@pytest.mark.asyncio
async def test_logger_add_event(async_session, logger):
    svc = await create_service(async_session)

    log = await logger.log_event(
        session=async_session,
        service_id=svc.id,
        event_type="info",
        message="Hello",
    )

    assert log.service_id == svc.id
    assert log.event_type == "info"
    assert log.message == "Hello"


@pytest.mark.asyncio
async def test_logger_get_logs(async_session, logger):
    svc = await create_service(async_session)

    await logger.log_event(async_session, svc.id, "info", "A")
    await logger.log_event(async_session, svc.id, "error", "B")

    logs = await logger.get_logs(async_session, svc.id)

    assert len(logs) == 2


@pytest.mark.asyncio
async def test_logger_get_logs_filtered(async_session, logger):
    svc = await create_service(async_session)

    await logger.log_event(async_session, svc.id, "info", "A")
    await logger.log_event(async_session, svc.id, "error", "B")

    logs = await logger.get_logs(async_session, svc.id, event_type="info")

    assert len(logs) == 1
    assert logs[0].event_type == "info"
