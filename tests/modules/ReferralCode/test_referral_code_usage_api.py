import uuid
from datetime import datetime

from httpx import AsyncClient

from backend.ReferralCode.models import ReferralCode, ReferralCodeUsage


async def create_code(session):
    code = ReferralCode(
        id=uuid.uuid4(),
        code="USEME-123",
        user_id=uuid.uuid4(),
        service_id=uuid.uuid4(),
        is_active=True,
    )
    session.add(code)
    await session.flush()
    return code


async def create_usage(session, code_id, user_id):
    rec = ReferralCodeUsage(
        id=uuid.uuid4(),
        referral_code_id=code_id,
        used_by_user_id=user_id,
        used_at=datetime.utcnow(),
    )
    session.add(rec)
    await session.flush()
    return rec


async def test_get_usage_history(async_client: AsyncClient, async_session):
    code = await create_code(async_session)

    u1 = uuid.uuid4()
    u2 = uuid.uuid4()

    await create_usage(async_session, code.id, u1)
    await create_usage(async_session, code.id, u2)
    await async_session.commit()

    response = await async_client.get(
        f"/referral-codes/history/{code.id}",
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["referral_code_id"] == str(code.id)


async def test_clear_usage_history(async_client: AsyncClient, async_session):
    code = await create_code(async_session)
    await create_usage(async_session, code.id, uuid.uuid4())
    await async_session.commit()

    response = await async_client.delete(
        f"/referral-codes/history/{code.id}",
    )

    assert response.status_code == 200

    # Проверяем что очищено
    rows = await async_session.execute(
        ReferralCodeUsage.__table__.select(),
    )
    assert len(rows.fetchall()) == 0
