import json


class WebhookRetryService:
    def __init__(self, repo, webhook_client, logger):
        self.repo = repo
        self.client = webhook_client
        self.logger = logger

    async def retry_event(self, session, event_id):
        event = await self.repo.get_event(session, event_id)
        service = await self.repo.get_service(session, event.service_id)
        payload = json.loads(event.payload)

        success, status, response = await self.client.send(
            service.webhook_url, payload
        )

        await self.logger.log_attempt(
            session=session,
            service_id=service.id,
            url=service.webhook_url,
            payload=event.payload,
            status=status,
            response=response,
            success=success,
            attempt=event.attempt + 1,
        )

        return success

    async def retry_failed(self, session, service_id):
        failed = await self.repo.get_failed_events(session, service_id)
        service = await self.repo.get_service(session, service_id)

        results = []

        for event in failed:
            payload = json.loads(event.payload)

            success, status, response = await self.client.send(
                service.webhook_url, payload
            )

            await self.logger.log_attempt(
                session=session,
                service_id=service.id,
                url=service.webhook_url,
                payload=event.payload,
                status=status,
                response=response,
                success=success,
                attempt=event.attempt + 1,
            )

            results.append({"event": str(event.id), "success": success})

        return results
