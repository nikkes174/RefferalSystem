import uuid
from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.database.base import Base
from backend.ExternalService.models import ExternalService
from backend.Referral.models import Referral
from backend.Referral.service import ReferralService
from backend.User.models import User


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as s:
        yield s


@pytest.fixture
def service():
    return ReferralService()


async def create_svc(session):
    svc = ExternalService(
        id=uuid.uuid4(),
        service_name="svc",
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


async def create_ref(session, referrer, referred, svc, level=1):
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
async def test_service_stats(session, service):
    svc = await create_svc(session)
    a = await create_user(session, svc.id)
    b = await create_user(session, svc.id)

    await create_ref(session, a, b, svc, level=1)

    stats = await service.get_stats(session, svc.id)

    assert len(stats) == 1
    assert stats[0]["level"] == 1
    assert stats[0]["count"] == 1


@pytest.mark.asyncio
async def test_service_export_json(session, service):
    svc = await create_svc(session)
    a = await create_user(session, svc.id)
    b = await create_user(session, svc.id)

    await create_ref(session, a, b, svc)

    content = await service.export_referrals(session, svc.id, "json")
    assert '"referrer_id":' in content


@pytest.mark.asyncio
async def test_service_export_csv(session, service):
    svc = await create_svc(session)
    a = await create_user(session, svc.id)
    b = await create_user(session, svc.id)

    await create_ref(session, a, b, svc)

    content = await service.export_referrals(session, svc.id, "csv")

    assert "referrer_id" in content
    assert str(a.id) in content
