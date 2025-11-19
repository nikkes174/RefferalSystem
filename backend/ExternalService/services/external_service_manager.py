import uuid
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from backend.ExternalService.models import ExternalService
from backend.ExternalService.repository import ExternalServiceRepository
from backend.ExternalService.schemas import (
    ExternalServiceCreate,
    ExternalServiceUpdate,
)


class ExternalServiceManager:
    def __init__(self, repo: ExternalServiceRepository):
        self.repo = repo

    async def register_service(
        self,
        session: AsyncSession,
        data: ExternalServiceCreate,
    ):
        service = ExternalService(
            id=uuid.uuid4(),
            service_name=data.service_name,
            api_key=str(uuid.uuid4()),
            webhook_url=data.webhook_url,
        )

        return await self.repo.create_service(session, service)

    async def update_webhook(
        self,
        session: AsyncSession,
        service_id: UUID,
        data: ExternalServiceUpdate,
    ):
        return await self.repo.update_webhook(
            session=session,
            service_id=service_id,
            webhook_url=data.webhook_url,
        )

    async def archive_service(self, session: AsyncSession, service_id: UUID):
        return await self.repo.archive_service(session, service_id)

    async def get_service_by_id(self, session: AsyncSession, service_id: UUID):
        return await self.repo.get_by_id(session, service_id)

    async def get_service_by_api_key(
        self,
        session: AsyncSession,
        api_key: str,
    ):
        return await self.repo.get_by_api_key(session, api_key)
