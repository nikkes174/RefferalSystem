from backend.ExternalService.services.external_service_manager import (
    ExternalServiceManager,
)
from backend.ExternalService.services.webhook_client import WebhookClient
from backend.ExternalService.services.webhook_logger import WebhookLogger
from backend.ExternalService.services.webhook_retry import WebhookRetryService


class WebhookService:
    def __init__(self, repo):
        self.manager = ExternalServiceManager(repo)
        self.client = WebhookClient()
        self.logger = WebhookLogger(repo)
        self.retry = WebhookRetryService(repo, self.client, self.logger)
