import uuid
from datetime import datetime

from httpx import AsyncClient

from backend.ExternalService.models import ExternalService, WebhookEvent


async def create_service(session):
    svc = ExternalService(
        id=uuid.uuid4(),
        service_name="svc",
        api_key="123",
        webhook_url="https://example.com/hook",
        created_at=datetime.utcnow(),
    )
    session.add(svc)
    await session.flush()
    return svc


async def create_event(session, service_id, success=False):
    ev = WebhookEvent(
        id=uuid.uuid4(),
        service_id=service_id,
        url="https://example.com/hook",
        payload='{"a":1}',
        success=success,
        attempt=1,
    )
    session.add(ev)
    await session.flush()
    return ev


async def test_retry_single_webhook(async_client: AsyncClient, async_session):
    svc = await create_service(async_session)
    event = await create_event(async_session, svc.id, success=False)

    response = await async_client.post(
        f"/external-services/webhook/retry/{event.id}",
    )

    assert response.status_code == 200
    assert "success" in response.json()


async def test_retry_failed_webhooks(async_client: AsyncClient, async_session):
    svc = await create_service(async_session)

    await create_event(async_session, svc.id, success=False)
    await create_event(async_session, svc.id, success=False)

    response = await async_client.post(
        f"/external-services/webhook/retry-failed/{svc.id}",
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
