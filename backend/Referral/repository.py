from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.Referral.models import Referral


class ReferralRepository:
    async def create(self, session: AsyncSession, referral: Referral):
        session.add(referral)
        await session.flush()
        return referral

    async def get_user_referrals(
        self,
        session: AsyncSession,
        user_id: UUID,
        service_id: UUID,
    ):
        stmt = select(Referral).where(
            Referral.referrer_id == user_id,
            Referral.service_id == service_id,
        )
        res = await session.execute(stmt)
        return res.scalars().all()

    async def get_referral_parents(
        self,
        session: AsyncSession,
        user_id: UUID,
        service_id: UUID,
    ):
        stmt = select(Referral).where(
            Referral.referred_id == user_id,
            Referral.service_id == service_id,
        )
        res = await session.execute(stmt)
        return res.scalars().all()

    async def get_top_referrers(
        self,
        session: AsyncSession,
        service_id: UUID,
        limit: int = 10,
    ):
        from sqlalchemy import func

        stmt = (
            select(
                Referral.referrer_id,
                func.count(Referral.id).label("count"),
            )
            .where(Referral.service_id == service_id)
            .group_by(Referral.referrer_id)
            .order_by(func.count(Referral.id).desc())
            .limit(limit)
        )

        res = await session.execute(stmt)
        return res.all()

    async def get_referral_stats(self, session, service_id: UUID):

        stmt = (
            select(
                Referral.level,
                func.count(Referral.id).label("count"),
            )
            .where(Referral.service_id == service_id)
            .group_by(Referral.level)
            .order_by(Referral.level)
        )

        res = await session.execute(stmt)
        return res.all()

    async def get_all_referrals_for_export(self, session, service_id: UUID):
        """Получение всех рефералов сервиса для выгрузки."""
        stmt = select(Referral).where(Referral.service_id == service_id)
        res = await session.execute(stmt)
        return res.scalars().all()

    async def get_by_id(self, session: AsyncSession, referral_id: UUID):
        stmt = select(Referral).where(Referral.id == referral_id)
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    async def update_level(
        self, session: AsyncSession, referral_id: UUID, new_level: int
    ):
        referral = await self.get_by_id(session, referral_id)
        if not referral:
            return None

        referral.level = new_level
        await session.flush()
        return referral
