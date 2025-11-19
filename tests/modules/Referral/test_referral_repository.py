import uuid
from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.database.base import Base
from backend.ExternalService.models import ExternalService
from backend.Referral.models import Referral
from backend.Referral.repository import ReferralRepository
from backend.User.models import User


@pytest.fixture
async def session():
    """In-memory async SQLite session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as s:
        yield s


@pytest.fixture
def repo():
    return ReferralRepository()


async def create_service(session):
    svc = ExternalService(
        id=uuid.uuid4(),
        service_name="svc1",
        api_key="123",
        webhook_url=None,
        created_at=datetime.utcnow(),
    )
    session.add(svc)
    await session.flush()
    return svc


async def create_user(session, service_id):
    user = User(
        id=uuid.uuid4(),
        external_user_id=str(uuid.uuid4()),
        service_id=service_id,
        created_at=datetime.utcnow(),
    )
    session.add(user)
    await session.flush()
    return user


async def create_referral(session, referrer, referred, svc, level=1):
    ref = Referral(
        id=uuid.uuid4(),
        referrer_id=referrer.id,
        referred_id=referred.id,
        service_id=svc.id,
        referral_code_id=None,
        level=level,
        registered_at=datetime.utcnow(),
    )
    session.add(ref)
    await session.flush()
    return ref


@pytest.mark.asyncio
async def test_create_referral(repo, session):
    svc = await create_service(session)
    a = await create_user(session, svc.id)
    b = await create_user(session, svc.id)

    new_ref = Referral(
        id=uuid.uuid4(),
        referrer_id=a.id,
        referred_id=b.id,
        service_id=svc.id,
        level=1,
        referral_code_id=None,
    )

    res = await repo.create(session, new_ref)

    assert res.id == new_ref.id
    assert res.referrer_id == a.id
    assert res.referred_id == b.id


@pytest.mark.asyncio
async def test_get_user_referrals(repo, session):
    svc = await create_service(session)
    a = await create_user(session, svc.id)
    b = await create_user(session, svc.id)

    await create_referral(session, a, b, svc)

    result = await repo.get_user_referrals(session, a.id, svc.id)

    assert len(result) == 1
    assert result[0].referred_id == b.id


@pytest.mark.asyncio
async def test_get_referral_parents(repo, session):
    svc = await create_service(session)
    a = await create_user(session, svc.id)
    b = await create_user(session, svc.id)

    await create_referral(session, a, b, svc)

    result = await repo.get_referral_parents(session, b.id, svc.id)

    assert len(result) == 1
    assert result[0].referrer_id == a.id


@pytest.mark.asyncio
async def test_get_top_referrers(repo, session):
    svc = await create_service(session)

    a = await create_user(session, svc.id)
    b = await create_user(session, svc.id)
    c = await create_user(session, svc.id)

    # A invited B and C → should be top referrer
    await create_referral(session, a, b, svc)
    await create_referral(session, a, c, svc)

    result = await repo.get_top_referrers(session, svc.id, limit=1)

    assert len(result) == 1
    top_referrer, count = result[0]

    assert top_referrer == a.id
    assert count == 2
