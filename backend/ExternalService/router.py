from uuid import UUID
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

import backend.database.db as db_module
from backend.ExternalService.archive_service import ServiceArchiveManager
from backend.ExternalService.repository import ExternalServiceRepository
from backend.ExternalService.schemas import (
    ExternalServiceCreate,
    ExternalServiceRead,
    ExternalServiceUpdate,
    ServiceEventLogRead,
)
from backend.ExternalService.services.external_service_manager import (
    ExternalServiceManager,
)
from backend.ExternalService.services.webhook_client import WebhookClient
from backend.ExternalService.services.webhook_logger import WebhookLogger
from backend.ExternalService.services.webhook_retry import WebhookRetryService

router = APIRouter(prefix="/external-services", tags=["External Services"])

repo = ExternalServiceRepository()
logger = WebhookLogger(repo)
client = WebhookClient(http_client=httpx.AsyncClient())
manager = ExternalServiceManager(repo)
retry = WebhookRetryService(repo, client, logger)
archive_manager = ServiceArchiveManager(repo, logger)


async def get_session():
    async with db_module.db.get_session() as session:
        yield session


@router.post("/", response_model=ExternalServiceRead)
async def register_external_service(
    data: ExternalServiceCreate,
    session: AsyncSession = Depends(get_session),
):
    new_service = await manager.register_service(session, data)
    return new_service


@router.patch("/{service_id}/webhook", response_model=ExternalServiceRead)
async def update_webhook(
    service_id: UUID,
    data: ExternalServiceUpdate,
    session: AsyncSession = Depends(get_session),
):
    updated = await manager.update_webhook(session, service_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Service not found")
    return updated


@router.get("/by-api-key", response_model=ExternalServiceRead)
async def get_service_by_api_key(
    api_key: str,
    session: AsyncSession = Depends(get_session),
):
    result = await manager.get_service_by_api_key(session, api_key)
    if not result:
        raise HTTPException(status_code=404, detail="Invalid API key")
    return result


@router.post("/{service_id}/archive")
async def archive_service(
    service_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    result = await archive_manager.archive_service(session, service_id)
    return result


@router.post("/webhook/retry/{event_id}")
async def retry_single_webhook(
    event_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    ok = await retry.retry_single(session, event_id)
    return {"success": ok}


@router.post("/webhook/retry-failed/{service_id}")
async def retry_failed_webhooks(
    service_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    result = await retry.retry_failed(session, service_id)
    return result


@router.get("/logs/{service_id}", response_model=list[ServiceEventLogRead])
async def get_service_logs(
    service_id: UUID,
    event_type: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
):
    logs = await logger.get_logs(session, service_id, event_type)
    return logs
