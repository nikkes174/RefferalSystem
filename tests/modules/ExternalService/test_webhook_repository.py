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
        service_name="svc",
        api_key="123",
        webhook_url="https://test.com/hook",
        created_at=datetime.utcnow(),
    )
    session.add(svc)
    await session.flush()
    return svc


@pytest.mark.asyncio
async def test_log_webhook_attempt(repo, async_session):
    svc = await create_service(async_session)

    event = await repo.log_webhook_attempt(
        async_session,
        service_id=svc.id,
        url=svc.webhook_url,
        payload='{"x":1}',
        status=200,
        response="OK",
        success=True,
        attempt=1,
    )

    assert event.id is not None
    assert event.success is True


@pytest.mark.asyncio
async def test_get_event(repo, async_session):
    svc = await create_service(async_session)

    event = await repo.log_webhook_attempt(
        async_session,
        service_id=svc.id,
        url=svc.webhook_url,
        payload="{}",
        status=500,
        response="fail",
        success=False,
        attempt=1,
    )

    result = await repo.get_event(async_session, event.id)
    assert result.id == event.id


@pytest.mark.asyncio
async def test_get_failed_events(repo, async_session):
    svc = await create_service(async_session)

    await repo.log_webhook_attempt(
        async_session,
        svc.id,
        svc.webhook_url,
        "{}",
        200,
        "OK",
        True,
        1,
    )
    failed = await repo.log_webhook_attempt(
        async_session,
        svc.id,
        svc.webhook_url,
        "{}",
        None,
        "timeout",
        False,
        1,
    )

    rows = await repo.get_failed_events(async_session, svc.id)

    assert len(rows) == 1
    assert rows[0].id == failed.id
