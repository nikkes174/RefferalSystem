import uuid
from datetime import datetime

from httpx import AsyncClient

from backend.ExternalService.models import ExternalService, ServiceEventLog


async def create_service(session):
    svc = ExternalService(
        id=uuid.uuid4(),
        service_name="svc-api",
        api_key="xxx",
        webhook_url="https://example.com/hook",
        created_at=datetime.utcnow(),
    )
    session.add(svc)
    await session.flush()
    return svc


async def create_log(session, service_id, event_type="info", message="Test"):
    log = ServiceEventLog(
        id=uuid.uuid4(),
        service_id=service_id,
        event_type=event_type,
        message=message,
        created_at=datetime.utcnow(),
    )
    session.add(log)
    await session.flush()
    return log


async def test_api_get_logs(async_client: AsyncClient, async_session):
    svc = await create_service(async_session)

    await create_log(async_session, svc.id, "info", "A")
    await create_log(async_session, svc.id, "error", "B")

    res = await async_client.get(f"/external-services/logs/{svc.id}")
    assert res.status_code == 200

    data = res.json()
    assert len(data) == 2


async def test_api_get_logs_filtered(async_client: AsyncClient, async_session):
    svc = await create_service(async_session)

    await create_log(async_session, svc.id, "info", "A")
    await create_log(async_session, svc.id, "error", "B")

    res = await async_client.get(
        f"/external-services/logs/{svc.id}?event_type=error",
    )

    assert res.status_code == 200

    data = res.json()
    assert len(data) == 1
    assert data[0]["event_type"] == "error"
