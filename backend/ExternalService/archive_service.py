import uuid

from backend.ExternalService.models import (
    ArchivedReferralCode,
    ArchivedService,
    ArchivedWebhookEvent,
)
from backend.ExternalService.repository import ExternalServiceRepository
from backend.ExternalService.services.webhook_logger import WebhookLogger


class ServiceArchiveManager:

    def __init__(self, repo: ExternalServiceRepository, logger: WebhookLogger):
        self.repo = repo
        self.logger = logger

    async def archive_service(self, session, service_id: uuid.UUID):
        # 1) получить сервис
        service = await self.repo.get_service(session, service_id)
        if not service:
            raise ValueError("Service not found")

        archived = ArchivedService(
            id=uuid.uuid4(),
            original_service_id=service.id,
            service_name=service.service_name,
            api_key=service.api_key,
            webhook_url=service.webhook_url,
        )
        session.add(archived)

        # 3) архивировать реферальные коды
        codes = await self.repo.get_service_codes(session, service_id)
        for code in codes:
            session.add(
                ArchivedReferralCode(
                    id=uuid.uuid4(),
                    original_code_id=code.id,
                    service_id=service_id,
                    code=code.code,
                    created_at=code.created_at,
                    expires_at=code.expires_at,
                    is_active=code.is_active,
                ),
            )
            await session.delete(code)

        # 4) архивировать события webhook
        events = await self.repo.get_all_events(session, service_id)
        for ev in events:
            session.add(
                ArchivedWebhookEvent(
                    id=uuid.uuid4(),
                    original_event_id=ev.id,
                    service_id=service_id,
                    payload=ev.payload,
                    response_status=ev.response_status,
                    success=ev.success,
                    attempt=ev.attempt,
                    created_at=ev.created_at,
                ),
            )
            await session.delete(ev)

        await session.delete(service)

        await self.logger.log_event(
            session,
            service_id,
            event_type="archive",
            message=f"Service archived (name={service.service_name})",
        )

        return {"archived": True}
