from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.base import BaseRepository
from backend.ExternalService.models import (
    ExternalService,
    ServiceEventLog,
    WebhookEvent,
)


class ExternalServiceRepository(BaseRepository[ExternalService]):
    def __init__(self):
        super().__init__(ExternalService)

    async def create_service(
        self,
        session: AsyncSession,
        service: ExternalService,
    ):
        session.add(service)
        await session.flush()
        return service

    async def get_by_api_key(self, session: AsyncSession, api_key: str):
        stmt = select(ExternalService).where(
            ExternalService.api_key == api_key,
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_webhook(
        self,
        session: AsyncSession,
        service_id: UUID,
        webhook_url: str | None,
    ):
        stmt = (
            update(ExternalService)
            .where(ExternalService.id == service_id)
            .values(webhook_url=webhook_url)
            .returning(ExternalService)
        )

        result = await session.execute(stmt)
        await session.flush()
        return result.scalar_one_or_none()

    async def get_by_id(self, session: AsyncSession, service_id: UUID):
        return await session.get(ExternalService, service_id)

    async def archive_service(self, session: AsyncSession, service_id: UUID):
        stmt = (
            update(ExternalService)
            .where(ExternalService.id == service_id)
            .values(webhook_url=None)
            .returning(ExternalService)
        )
        result = await session.execute(stmt)
        await session.flush()
        return result.scalar_one_or_none()

    async def log_webhook_attempt(
        self,
        session,
        service_id,
        url,
        payload,
        status,
        response,
        success,
        attempt,
    ):
        event = WebhookEvent(
            service_id=service_id,
            url=url,
            payload=payload,
            response_status=status,
            response_body=response,
            success=success,
            attempt=attempt,
        )
        session.add(event)
        await session.flush()
        return event

    async def get_event(self, session, event_id):
        stmt = select(WebhookEvent).where(WebhookEvent.id == event_id)
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_failed_events(self, session, service_id):
        stmt = select(WebhookEvent).where(
            WebhookEvent.service_id == service_id,
            WebhookEvent.success == False,
        )
        res = await session.execute(stmt)
        return res.scalars().all()

    async def add_log(self, session, service_id, event_type, message):
        log = ServiceEventLog(
            service_id=service_id,
            event_type=event_type,
            message=message,
        )
        session.add(log)
        await session.flush()
        return log

    async def get_logs(self, session, service_id, event_type=None):
        stmt = select(ServiceEventLog).where(
            ServiceEventLog.service_id == service_id,
        )

        if event_type:
            stmt = stmt.where(ServiceEventLog.event_type == event_type)

        stmt = stmt.order_by(ServiceEventLog.created_at.desc())

        rows = await session.execute(stmt)
        return rows.scalars().all()
