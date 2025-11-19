from httpx import AsyncClient

from backend.ExternalService.services.webhook_client import WebhookClient

webhook_client = WebhookClient(AsyncClient())
