import csv
import json
import uuid
from io import StringIO
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from backend.Referral.models import Referral
from backend.Referral.repository import ReferralRepository
from backend.Referral.schemas import ReferralCreate


class ReferralService:
    def __init__(self):
        self.repo = ReferralRepository()

    async def _get_parent(
        self,
        session: AsyncSession,
        user_id: UUID,
        service_id: UUID,
    ):
        parents = await self.repo.get_referral_parents(
            session,
            user_id,
            service_id,
        )
        return parents[0] if parents else None

    async def _detect_cycle(
            self,
            session,
            referrer_id,
            referred_id,
            service_id,
    ):
        current = referred_id

        while True:
            parent = await self._get_parent(session, current, service_id)
            if not parent:
                return False

            if parent.referrer_id == referrer_id:
                return True

            if parent.referrer_id == referred_id:
                return True

            current = parent.referrer_id

    async def _calculate_level(
        self,
        session: AsyncSession,
        referrer_id: UUID,
        service_id: UUID,
    ):
        parent = await self._get_parent(session, referrer_id, service_id)
        if not parent:
            return 1
        return parent.level + 1

    async def register_referral(self, session: AsyncSession, data: ReferralCreate):
        cycle = await self._detect_cycle(
            session,
            referrer_id=data.referrer_id,
            referred_id=data.referred_id,
            service_id=data.service_id,
        )
        if cycle:
            raise ValueError("Cycle detected")

        level = await self._calculate_level(
            session,
            data.referrer_id,
            data.service_id,
        )

        new_ref = Referral(
            id=uuid.uuid4(),
            referrer_id=data.referrer_id,
            referred_id=data.referred_id,
            service_id=data.service_id,
            referral_code_id=data.referral_code_id,
            level=level,
        )

        await session.flush()
        return await self.repo.create(session, new_ref)

    async def get_user_referrals(
        self,
        session: AsyncSession,
        user_id: UUID,
        service_id: UUID,
    ):
        return await self.repo.get_user_referrals(session, user_id, service_id)

    async def get_parent_chain(self, session, user_id, service_id):
        parent = await self._get_parent(session, user_id, service_id)
        return [parent] if parent else []

    async def get_top_referrers(
        self,
        session: AsyncSession,
        service_id: UUID,
        limit=10,
    ):
        return await self.repo.get_top_referrers(session, service_id, limit)

    async def get_stats(self, session, service_id: UUID):
        data = await self.repo.get_referral_stats(session, service_id)
        return [{"level": lvl, "count": cnt} for lvl, cnt in data]

    async def export_referrals(self, session, service_id: UUID, format: str):
        refs = await self.repo.get_all_referrals_for_export(
            session, service_id
        )

        rows = [
            {
                "id": str(r.id),
                "referrer_id": str(r.referrer_id),
                "referred_id": str(r.referred_id),
                "service_id": str(r.service_id),
                "level": r.level,
                "registered_at": r.registered_at.isoformat(),
                "referral_code_id": (
                    str(r.referral_code_id) if r.referral_code_id else None
                ),
            }
            for r in refs
        ]

        if format == "json":
            return json.dumps(rows, ensure_ascii=False, indent=4)

        if format == "csv":
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
            return output.getvalue()

        raise ValueError("Invalid export format")

    async def force_update_level(
        self,
        session: AsyncSession,
        referral_id: UUID,
        new_level: int,
    ):

        if new_level < 1:
            raise ValueError("Level must be >= 1")

        referral = await self.repo.update_level(
            session, referral_id, new_level
        )
        if not referral:
            raise ValueError("Referral not found")

        return referral
