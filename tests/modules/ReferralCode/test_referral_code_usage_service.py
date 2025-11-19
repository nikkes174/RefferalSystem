import uuid

import pytest

from backend.ReferralCode.models import ReferralCode, ReferralCodeUsage
from backend.ReferralCode.service import ReferralCodeService


@pytest.fixture
def service():
    return ReferralCodeService()


async def create_code(session):
    rc = ReferralCode(
        id=uuid.uuid4(),
        code="SERVICE-TEST",
        user_id=uuid.uuid4(),
        service_id=uuid.uuid4(),
        is_active=True,
    )
    session.add(rc)
    await session.flush()
    return rc


@pytest.mark.asyncio
async def test_log_usage(session, service):
    code = await create_code(session)
    user_id = uuid.uuid4()

    rec = await service.log_usage(session, code.id, user_id)

    assert rec.referral_code_id == code.id
    assert rec.used_by_user_id == user_id


@pytest.mark.asyncio
async def test_get_usage_history(session, service):
    code = await create_code(session)

    u1 = uuid.uuid4()
    u2 = uuid.uuid4()

    await service.log_usage(session, code.id, u1)
    await service.log_usage(session, code.id, u2)

    rows = await service.get_usage_history(session, code.id)

    assert len(rows) == 2
    assert rows[0].referral_code_id == code.id


@pytest.mark.asyncio
async def test_clear_usage(session, service):
    code = await create_code(session)

    await service.log_usage(session, code.id, uuid.uuid4())
    await session.commit()

    await service.clear_usage(session, code.id)
    await session.commit()

    rows = await session.execute(ReferralCodeUsage.__table__.select())
    assert len(rows.fetchall()) == 0
