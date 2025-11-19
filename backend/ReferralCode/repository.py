from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ReferralCode.models import ReferralCode, ReferralCodeUsage


class ReferralCodeRepository:
    async def create(self, session: AsyncSession, code: ReferralCode):
        session.add(code)
        await session.flush()
        return code

    async def get_by_id(self, session: AsyncSession, code_id: UUID):
        return await session.get(ReferralCode, code_id)

    async def get_by_code(self, session: AsyncSession, code: str):
        stmt = select(ReferralCode).where(ReferralCode.code == code)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_external(
        self,
        session: AsyncSession,
        external_user_id: str,
    ):
        from backend.User.models import User

        stmt = (
            select(ReferralCode)
            .join(User)
            .where(User.external_user_id == external_user_id)
        )

        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_all_by_service(
        self,
        session: AsyncSession,
        service_id: UUID,
    ):
        stmt = select(ReferralCode).where(
            ReferralCode.service_id == service_id,
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def deactivate(self, session: AsyncSession, code_id: UUID):
        stmt = (
            update(ReferralCode)
            .where(ReferralCode.id == code_id)
            .values(is_active=False)
            .returning(ReferralCode)
        )
        result = await session.execute(stmt)
        await session.flush()
        return result.scalar_one_or_none()

    async def update_limits(
        self,
        session: AsyncSession,
        code_id: UUID,
        expires_at: datetime | None,
        usage_limit: int | None,
    ):
        stmt = (
            update(ReferralCode)
            .where(ReferralCode.id == code_id)
            .values(
                expires_at=expires_at,
                usage_limit=usage_limit,
            )
            .returning(ReferralCode)
        )
        result = await session.execute(stmt)
        await session.flush()
        return result.scalar_one_or_none()

    async def get_inactive(self, session: AsyncSession, service_id: UUID):
        stmt = select(ReferralCode).where(
            ReferralCode.service_id == service_id,
            ReferralCode.is_active == False,
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def add_usage(self, session, code_id: UUID, user_id: UUID):
        record = ReferralCodeUsage(
            referral_code_id=code_id,
            used_by_user_id=user_id,
        )
        session.add(record)
        await session.flush()
        return record

    async def get_usage_history(self, session, code_id: UUID):
        stmt = (
            select(ReferralCodeUsage)
            .where(
                ReferralCodeUsage.referral_code_id == code_id,
            )
            .order_by(ReferralCodeUsage.used_at)
        )
        res = await session.execute(stmt)
        return res.scalars().all()

    async def clear_usage_history(self, session, code_id: UUID):
        stmt = delete(ReferralCodeUsage).where(
            ReferralCodeUsage.referral_code_id == code_id,
        )
        await session.execute(stmt)
