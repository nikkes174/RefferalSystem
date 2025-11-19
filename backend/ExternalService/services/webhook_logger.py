from backend.ExternalService.repository import ExternalServiceRepository


class WebhookLogger:
    def __init__(self, repo: ExternalServiceRepository):
        self.repo = repo

    async def log_attempt(
        self,
        session,
        *,
        service_id,
        url,
        payload,
        status,
        response,
        success,
        attempt,
    ):
        await self.repo.log_webhook_attempt(
            session=session,
            service_id=service_id,
            url=url,
            payload=payload,
            status=status,
            response=response,
            success=success,
            attempt=attempt,
        )

    async def log_event(self, session, service_id, event_type, message):
        return await self.repo.add_log(
            session, service_id, event_type, message
        )

    async def get_logs(self, session, service_id, event_type=None):
        return await self.repo.get_logs(session, service_id, event_type)
