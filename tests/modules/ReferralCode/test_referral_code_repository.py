import uuid
from datetime import datetime, timedelta

import pytest

from backend.ReferralCode.models import ReferralCode
from backend.ReferralCode.repository import ReferralCodeRepository
from backend.User.models import User


@pytest.mark.asyncio
async def test_create_referral_code(session):
    repo = ReferralCodeRepository()

    code = ReferralCode(
        id=uuid.uuid4(),
        code="TEST123",
        user_id=uuid.uuid4(),
        service_id=uuid.uuid4(),
        is_active=True,
    )

    created = await repo.create(session, code)

    assert created.code == "TEST123"

    db_obj = await session.get(ReferralCode, created.id)
    assert db_obj is not None


@pytest.mark.asyncio
async def test_get_by_id(session):
    repo = ReferralCodeRepository()

    rc = ReferralCode(
        id=uuid.uuid4(),
        code="BYID",
        user_id=uuid.uuid4(),
        service_id=uuid.uuid4(),
    )
    session.add(rc)
    await session.flush()

    found = await repo.get_by_id(session, rc.id)

    assert found is not None
    assert found.code == "BYID"


@pytest.mark.asyncio
async def test_get_by_code(session):
    repo = ReferralCodeRepository()

    rc = ReferralCode(
        id=uuid.uuid4(),
        code="FINDME",
        user_id=uuid.uuid4(),
        service_id=uuid.uuid4(),
    )
    session.add(rc)
    await session.flush()

    found = await repo.get_by_code(session, "FINDME")

    assert found is not None
    assert found.code == "FINDME"


@pytest.mark.asyncio
async def test_get_by_user_external(session):
    repo = ReferralCodeRepository()

    # Создаем пользователя
    user = User(
        id=uuid.uuid4(),
        external_user_id="ext-123",
        service_id=uuid.uuid4(),
    )
    session.add(user)
    await session.flush()

    # Создаем 2 кода для него
    rc1 = ReferralCode(
        id=uuid.uuid4(),
        code="U1",
        user_id=user.id,
        service_id=user.service_id,
    )
    rc2 = ReferralCode(
        id=uuid.uuid4(),
        code="U2",
        user_id=user.id,
        service_id=user.service_id,
    )
    session.add_all([rc1, rc2])
    await session.flush()

    found = await repo.get_by_user_external(session, "ext-123")

    assert len(found) == 2
    assert {c.code for c in found} == {"U1", "U2"}


@pytest.mark.asyncio
async def test_get_all_by_service(session):
    repo = ReferralCodeRepository()
    sid = uuid.uuid4()

    rc1 = ReferralCode(
        id=uuid.uuid4(),
        code="S1",
        user_id=uuid.uuid4(),
        service_id=sid,
    )
    rc2 = ReferralCode(
        id=uuid.uuid4(),
        code="S2",
        user_id=uuid.uuid4(),
        service_id=sid,
    )
    session.add_all([rc1, rc2])
    await session.flush()

    found = await repo.get_all_by_service(session, sid)

    assert len(found) == 2
    assert {c.code for c in found} == {"S1", "S2"}


@pytest.mark.asyncio
async def test_deactivate(session):
    repo = ReferralCodeRepository()

    rc = ReferralCode(
        id=uuid.uuid4(),
        code="ACTIVE",
        user_id=uuid.uuid4(),
        service_id=uuid.uuid4(),
        is_active=True,
    )
    session.add(rc)
    await session.flush()

    updated = await repo.deactivate(session, rc.id)

    assert updated is not None
    assert updated.is_active is False


@pytest.mark.asyncio
async def test_update_limits(session):
    repo = ReferralCodeRepository()

    rc = ReferralCode(
        id=uuid.uuid4(),
        code="LIMIT",
        user_id=uuid.uuid4(),
        service_id=uuid.uuid4(),
    )
    session.add(rc)
    await session.flush()

    new_exp = datetime.utcnow() + timedelta(days=7)

    updated = await repo.update_limits(
        session=session,
        code_id=rc.id,
        expires_at=new_exp,
        usage_limit=10,
    )

    assert updated is not None
    assert updated.expires_at == new_exp
    assert updated.usage_limit == 10


@pytest.mark.asyncio
async def test_get_inactive(session):
    repo = ReferralCodeRepository()
    sid = uuid.uuid4()

    rc1 = ReferralCode(
        id=uuid.uuid4(),
        code="A1",
        user_id=uuid.uuid4(),
        service_id=sid,
        is_active=False,
    )
    rc2 = ReferralCode(
        id=uuid.uuid4(),
        code="A2",
        user_id=uuid.uuid4(),
        service_id=sid,
        is_active=False,
    )
    rc3 = ReferralCode(
        id=uuid.uuid4(),
        code="B3",
        user_id=uuid.uuid4(),
        service_id=uuid.uuid4(),
        is_active=False,
    )

    session.add_all([rc1, rc2, rc3])
    await session.flush()

    found = await repo.get_inactive(session, sid)

    assert len(found) == 2
    assert {c.code for c in found} == {"A1", "A2"}
