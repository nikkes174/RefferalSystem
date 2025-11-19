import uuid
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from backend.ExternalService.models import ExternalService, WebhookEvent
from backend.ExternalService.repository import ExternalServiceRepository
from backend.ExternalService.services.webhook_client import WebhookClient
from backend.ExternalService.services.webhook_logger import WebhookLogger
from backend.ExternalService.services.webhook_retry import WebhookRetryService


@pytest.fixture
def repo():
    return ExternalServiceRepository()


@pytest.fixture
def client():
    return WebhookClient(http_client=None)


@pytest.fixture
def logger(repo):
    return WebhookLogger(repo)


@pytest.fixture
def retry(repo, client, logger):
    return WebhookRetryService(repo, client, logger)


async def create_service(session):
    svc = ExternalService(
        id=uuid.uuid4(),
        service_name="retry",
        api_key="abc",
        webhook_url="https://test.com/hook",
        created_at=datetime.utcnow(),
    )
    session.add(svc)
    await session.flush()
    return svc


async def create_event(session, service_id):
    ev = WebhookEvent(
        id=uuid.uuid4(),
        service_id=service_id,
        url="https://test.com/hook",
        payload='{"x":1}',
        success=False,
        attempt=1,
    )
    session.add(ev)
    await session.flush()
    return ev


@pytest.mark.asyncio
async def test_retry_single(async_session, retry):
    svc = await create_service(async_session)
    ev = await create_event(async_session, svc.id)

    with patch(
        "backend.ExternalService.webhook_client.httpx.AsyncClient.post",
        new=AsyncMock(),
    ) as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = "OK"

        ok = await retry.retry_single(async_session, ev.id)

    assert ok is True


@pytest.mark.asyncio
async def test_retry_failed(async_session, retry):
    svc = await create_service(async_session)

    await create_event(async_session, svc.id)
    await create_event(async_session, svc.id)

    with patch(
        "backend.ExternalService.webhook_client.httpx.AsyncClient.post",
        new=AsyncMock(),
    ) as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = "OK"

        res = await retry.retry_failed(async_session, svc.id)

    assert len(res) == 2
    assert all(r["success"] is True for r in res)
