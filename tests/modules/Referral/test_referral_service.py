import uuid
from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.database.base import Base
from backend.ExternalService.models import ExternalService
from backend.Referral.schemas import ReferralCreate
from backend.Referral.service import ReferralService
from backend.User.models import User


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async_session = sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as s:
        yield s


@pytest.fixture
def service():
    return ReferralService()


async def create_user(session, service_id):
    user = User(
        id=uuid.uuid4(),
        external_user_id=str(uuid.uuid4()),
        service_id=service_id,
    )
    session.add(user)
    await session.flush()
    return user


async def create_service(session):
    service = ExternalService(
        id=uuid.uuid4(),
        service_name="test",
        api_key="123",
        webhook_url=None,
        created_at=datetime.utcnow(),
    )
    session.add(service)
    await session.flush()
    return service


@pytest.mark.asyncio
async def test_register_referral_level_1(session, service):
    svc = await create_service(session)
    referrer = await create_user(session, svc.id)
    referred = await create_user(session, svc.id)

    data = ReferralCreate(
        referrer_id=referrer.id,
        referred_id=referred.id,
        service_id=svc.id,
        referral_code_id=None,
    )

    result = await service.register_referral(session, data)

    assert result.level == 1
    assert result.referrer_id == referrer.id
    assert result.referred_id == referred.id


@pytest.mark.asyncio
async def test_register_referral_level_2(session, service):
    svc = await create_service(session)

    a = await create_user(session, svc.id)
    b = await create_user(session, svc.id)
    c = await create_user(session, svc.id)

    # A → B
    await service.register_referral(
        session,
        ReferralCreate(
            referrer_id=a.id,
            referred_id=b.id,
            service_id=svc.id,
            referral_code_id=None,
        ),
    )

    # B → C
    result = await service.register_referral(
        session,
        ReferralCreate(
            referrer_id=b.id,
            referred_id=c.id,
            service_id=svc.id,
            referral_code_id=None,
        ),
    )

    assert result.level == 2


@pytest.mark.asyncio
async def test_cycle_detection(session, service):
    svc = await create_service(session)

    a = await create_user(session, svc.id)
    b = await create_user(session, svc.id)

    # A → B
    await service.register_referral(
        session,
        ReferralCreate(
            referrer_id=a.id,
            referred_id=b.id,
            service_id=svc.id,
            referral_code_id=None,
        ),
    )

    # B → A must create cycle → error
    with pytest.raises(ValueError):
        await service.register_referral(
            session,
            ReferralCreate(
                referrer_id=b.id,
                referred_id=a.id,
                service_id=svc.id,
                referral_code_id=None,
            ),
        )


@pytest.mark.asyncio
async def test_get_user_referrals(session, service):
    svc = await create_service(session)

    a = await create_user(session, svc.id)
    b = await create_user(session, svc.id)

    await service.register_referral(
        session,
        ReferralCreate(
            referrer_id=a.id,
            referred_id=b.id,
            service_id=svc.id,
            referral_code_id=None,
        ),
    )

    children = await service.get_user_referrals(session, a.id, svc.id)

    assert len(children) == 1
    assert children[0].referred_id == b.id


@pytest.mark.asyncio
async def test_get_parent_chain(session, service):
    svc = await create_service(session)

    a = await create_user(session, svc.id)
    b = await create_user(session, svc.id)
    c = await create_user(session, svc.id)

    await service.register_referral(
        session,
        ReferralCreate(
            referrer_id=a.id,
            referred_id=b.id,
            service_id=svc.id,
            referral_code_id=None,
        ),
    )

    # B → C
    await service.register_referral(
        session,
        ReferralCreate(
            referrer_id=b.id,
            referred_id=c.id,
            service_id=svc.id,
            referral_code_id=None,
        ),
    )

    chain = await service.get_parent_chain(session, c.id, svc.id)

    assert len(chain) == 1
    assert chain[0].referrer_id == b.id


@pytest.mark.asyncio
async def test_get_top_referrers(session, service):
    svc = await create_service(session)

    a = await create_user(session, svc.id)
    b = await create_user(session, svc.id)
    c = await create_user(session, svc.id)

    # A invited B and C → top referrer
    await service.register_referral(
        session,
        ReferralCreate(
            referrer_id=a.id,
            referred_id=b.id,
            service_id=svc.id,
            referral_code_id=None,
        ),
    )
    await service.register_referral(
        session,
        ReferralCreate(
            referrer_id=a.id,
            referred_id=c.id,
            service_id=svc.id,
            referral_code_id=None,
        ),
    )

    top = await service.get_top_referrers(session, svc.id, limit=1)

    assert len(top) == 1
    assert top[0].referrer_id == a.id
