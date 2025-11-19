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


async def create_user(session, svc_id):
    user = User(
        id=uuid.uuid4(),
        external_user_id=str(uuid.uuid4()),
        service_id=svc_id,
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
async def test_repo_stats(repo, session):
    svc = await create_svc(session)
    a = await create_user(session, svc.id)
    b = await create_user(session, svc.id)

    await create_ref(session, a, b, svc, level=1)

    result = await repo.get_referral_stats(session, svc.id)

    assert len(result) == 1
    lvl, cnt = result[0]
    assert lvl == 1
    assert cnt == 1


@pytest.mark.asyncio
async def test_repo_export_list(repo, session):
    svc = await create_svc(session)
    a = await create_user(session, svc.id)
    b = await create_user(session, svc.id)

    await create_ref(session, a, b, svc)

    rows = await repo.get_all_referrals_for_export(session, svc.id)

    assert len(rows) == 1
    assert rows[0].referrer_id == a.id
