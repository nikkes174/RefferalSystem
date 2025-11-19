import random
import string
import uuid
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from backend.ReferralCode.models import ReferralCode
from backend.ReferralCode.repository import ReferralCodeRepository
from backend.ReferralCode.schemas import ReferralCodeCreate, ReferralCodeUpdate


class ReferralCodeService:
    def __init__(self):
        self.repo = ReferralCodeRepository()

    def _generate_code(self) -> str:
        """Генерирует код вида ABC123-XYZ."""
        part1 = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=6),
        )
        part2 = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=3),
        )
        return f"{part1}-{part2}"

    async def create_code(
        self,
        session: AsyncSession,
        data: ReferralCodeCreate,
    ):
        code_str = self._generate_code()

        new_code = ReferralCode(
            id=uuid.uuid4(),
            code=code_str,
            user_id=data.user_id,
            service_id=data.service_id,
            expires_at=data.expires_at,
            usage_limit=data.usage_limit,
        )
        return await self.repo.create(session, new_code)

    async def validate_code(self, session: AsyncSession, code: str):
        code_obj = await self.repo.get_by_code(session, code)

        if not code_obj:
            raise ValueError("Invalid code")

        if not code_obj.is_active:
            raise ValueError("Code is not active")

        if code_obj.expires_at and code_obj.expires_at < datetime.utcnow():
            raise ValueError("Code expired")

        return code_obj

    async def deactivate_code(self, session: AsyncSession, code_id: UUID):
        return await self.repo.deactivate(session, code_id)

    async def update_limits(
        self,
        session: AsyncSession,
        code_id: UUID,
        data: ReferralCodeUpdate,
    ):
        return await self.repo.update_limits(
            session,
            code_id=code_id,
            expires_at=data.expires_at,
            usage_limit=data.usage_limit,
        )

    async def mass_generate(
        self,
        session: AsyncSession,
        user_id: UUID,
        service_id: UUID,
        count: int,
    ):
        codes = []

        for _ in range(count):
            code = ReferralCode(
                id=uuid.uuid4(),
                code=self._generate_code(),
                user_id=user_id,
                service_id=service_id,
            )
            session.add(code)
            codes.append(code)

        await session.flush()
        return codes

    async def get_codes_by_service(
        self,
        session: AsyncSession,
        service_id: UUID,
    ):
        return await self.repo.get_all_by_service(session, service_id)

    async def get_by_user_external(
        self,
        session: AsyncSession,
        external_user_id: str,
    ):
        return await self.repo.get_by_user_external(session, external_user_id)

    async def get_inactive_codes(
        self,
        session: AsyncSession,
        service_id: UUID,
    ):
        return await self.repo.get_inactive(session, service_id)

    async def log_usage(self, session, code_id: UUID, user_id: UUID):
        return await self.repo.add_usage(session, code_id, user_id)

    async def get_usage_history(self, session, code_id: UUID):
        return await self.repo.get_usage_history(session, code_id)

    async def clear_usage(self, session, code_id: UUID):
        await self.repo.clear_usage_history(session, code_id)
