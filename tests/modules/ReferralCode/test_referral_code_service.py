import uuid
from datetime import datetime, timedelta

import pytest

from backend.ReferralCode.models import ReferralCode
from backend.ReferralCode.schemas import ReferralCodeCreate, ReferralCodeUpdate
from backend.ReferralCode.service import ReferralCodeService
from backend.User.models import User


@pytest.fixture
def service():
    return ReferralCodeService()


@pytest.mark.asyncio
async def test_generate_code_format(service):
    code = service._generate_code()
    # Формат: XXXXXXX-XXX
    assert "-" in code
    part1, part2 = code.split("-")
    assert len(part1) == 6
    assert len(part2) == 3


@pytest.mark.asyncio
async def test_create_code(session, service):
    data = ReferralCodeCreate(
        user_id=uuid.uuid4(),
        service_id=uuid.uuid4(),
        expires_at=None,
        usage_limit=None,
    )

    created = await service.create_code(session, data)

    assert created is not None
    assert created.user_id == data.user_id
    assert created.service_id == data.service_id
    assert created.code is not None

    from_db = await session.get(ReferralCode, created.id)
    assert from_db is not None


@pytest.mark.asyncio
async def test_validate_code_success(session, service):
    rc = ReferralCode(
        id=uuid.uuid4(),
        code="VALID123-ABC",
        user_id=uuid.uuid4(),
        service_id=uuid.uuid4(),
        is_active=True,
    )
    session.add(rc)
    await session.flush()

    result = await service.validate_code(session, rc.code)

    assert result.id == rc.id


@pytest.mark.asyncio
async def test_validate_code_not_found(session, service):
    with pytest.raises(ValueError, match="Invalid code"):
        await service.validate_code(session, "NOPE")


@pytest.mark.asyncio
async def test_validate_code_inactive(session, service):
    rc = ReferralCode(
        id=uuid.uuid4(),
        code="INACTIVE-1",
        user_id=uuid.uuid4(),
        service_id=uuid.uuid4(),
        is_active=False,
    )
    session.add(rc)
    await session.flush()

    with pytest.raises(ValueError, match="Code is not active"):
        await service.validate_code(session, rc.code)


@pytest.mark.asyncio
async def test_validate_code_expired(session, service):
    rc = ReferralCode(
        id=uuid.uuid4(),
        code="EXPIRED-1",
        user_id=uuid.uuid4(),
        service_id=uuid.uuid4(),
        is_active=True,
        expires_at=datetime.utcnow() - timedelta(hours=1),
    )
    session.add(rc)
    await session.flush()

    with pytest.raises(ValueError, match="Code expired"):
        await service.validate_code(session, rc.code)


@pytest.mark.asyncio
async def test_deactivate(session, service):
    rc = ReferralCode(
        id=uuid.uuid4(),
        code="TO-DEACT",
        user_id=uuid.uuid4(),
        service_id=uuid.uuid4(),
        is_active=True,
    )
    session.add(rc)
    await session.flush()

    updated = await service.deactivate_code(session, rc.id)

    assert updated.is_active is False


@pytest.mark.asyncio
async def test_update_limits(session, service):
    rc = ReferralCode(
        id=uuid.uuid4(),
        code="LIMITS",
        user_id=uuid.uuid4(),
        service_id=uuid.uuid4(),
    )
    session.add(rc)
    await session.flush()

    new_expire = datetime.utcnow() + timedelta(days=7)
    update_data = ReferralCodeUpdate(
        expires_at=new_expire,
        usage_limit=10,
    )

    updated = await service.update_limits(session, rc.id, update_data)

    assert updated.expires_at == new_expire
    assert updated.usage_limit == 10


@pytest.mark.asyncio
async def test_mass_generate(session, service):
    user_id = uuid.uuid4()
    service_id = uuid.uuid4()

    codes = await service.mass_generate(session, user_id, service_id, count=5)

    assert len(codes) == 5
    assert all(c.user_id == user_id for c in codes)
    assert all(c.service_id == service_id for c in codes)


@pytest.mark.asyncio
async def test_get_codes_by_service(session, service):
    sid = uuid.uuid4()

    c1 = ReferralCode(
        id=uuid.uuid4(),
        code="S1",
        user_id=uuid.uuid4(),
        service_id=sid,
    )
    c2 = ReferralCode(
        id=uuid.uuid4(),
        code="S2",
        user_id=uuid.uuid4(),
        service_id=sid,
    )
    session.add_all([c1, c2])
    await session.flush()

    found = await service.get_codes_by_service(session, sid)

    assert len(found) == 2


@pytest.mark.asyncio
async def test_get_by_user_external(session, service):
    user = User(
        id=uuid.uuid4(),
        external_user_id="ext-555",
        service_id=uuid.uuid4(),
    )
    session.add(user)
    await session.flush()

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

    found = await service.get_by_user_external(session, "ext-555")

    assert len(found) == 2


@pytest.mark.asyncio
async def test_get_inactive_codes(session, service):
    sid = uuid.uuid4()

    rc1 = ReferralCode(
        id=uuid.uuid4(),
        code="I1",
        user_id=uuid.uuid4(),
        service_id=sid,
        is_active=False,
    )
    rc2 = ReferralCode(
        id=uuid.uuid4(),
        code="I2",
        user_id=uuid.uuid4(),
        service_id=sid,
        is_active=False,
    )
    rc3 = ReferralCode(
        id=uuid.uuid4(),
        code="ACT",
        user_id=uuid.uuid4(),
        service_id=sid,
        is_active=True,
    )

    session.add_all([rc1, rc2, rc3])
    await session.flush()

    found = await service.get_inactive_codes(session, sid)

    assert len(found) == 2
    assert {c.code for c in found} == {"I1", "I2"}
