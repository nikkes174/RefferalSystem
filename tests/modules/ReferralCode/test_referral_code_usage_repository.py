import uuid
from datetime import datetime

import pytest

from backend.ReferralCode.models import ReferralCode, ReferralCodeUsage
from backend.ReferralCode.repository import ReferralCodeRepository


@pytest.fixture
def repo():
    return ReferralCodeRepository()


async def create_code(session):
    rc = ReferralCode(
        id=uuid.uuid4(),
        code="REPO-CODE",
        user_id=uuid.uuid4(),
        service_id=uuid.uuid4(),
        is_active=True,
    )
    session.add(rc)
    await session.flush()
    return rc


@pytest.mark.asyncio
async def test_add_usage(repo, session):
    code = await create_code(session)
    user_id = uuid.uuid4()

    rec = await repo.add_usage(session, code.id, user_id)

    assert rec.referral_code_id == code.id
    assert rec.used_by_user_id == user_id


@pytest.mark.asyncio
async def test_get_usage_history(repo, session):
    code = await create_code(session)

    r1 = ReferralCodeUsage(
        id=uuid.uuid4(),
        referral_code_id=code.id,
        used_by_user_id=uuid.uuid4(),
        used_at=datetime.utcnow(),
    )
    r2 = ReferralCodeUsage(
        id=uuid.uuid4(),
        referral_code_id=code.id,
        used_by_user_id=uuid.uuid4(),
        used_at=datetime.utcnow(),
    )

    session.add_all([r1, r2])
    await session.flush()

    rows = await repo.get_usage_history(session, code.id)

    assert len(rows) == 2


@pytest.mark.asyncio
async def test_clear_usage_history(repo, session):
    code = await create_code(session)

    r1 = ReferralCodeUsage(
        id=uuid.uuid4(),
        referral_code_id=code.id,
        used_by_user_id=uuid.uuid4(),
    )
    session.add(r1)
    await session.flush()

    await repo.clear_usage_history(session, code.id)

    rows = await session.execute(ReferralCodeUsage.__table__.select())
    assert len(rows.fetchall()) == 0
