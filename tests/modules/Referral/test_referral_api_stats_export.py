import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.database.base import Base
from backend.ExternalService.models import ExternalService
from backend.Referral.models import Referral
from backend.User.models import User
from main import app


@pytest.fixture(scope="function")
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as s:
        yield s


@pytest.fixture(scope="function")
def client():
    return TestClient(app)


async def create_service(session):
    svc = ExternalService(
        id=uuid.uuid4(),
        service_name="test_svc",
        api_key="xyz",
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
async def test_referral_stats(client, session):
    svc = await create_service(session)
    a = await create_user(session, svc.id)
    b = await create_user(session, svc.id)
    c = await create_user(session, svc.id)

    await create_ref(session, a, b, svc, level=1)
    await create_ref(session, b, c, svc, level=2)

    response = client.get(f"/referrals/stats/{svc.id}")
    assert response.status_code == 200

    stats = response.json()
    assert len(stats) == 2
    assert stats[0]["level"] == 1
    assert stats[0]["count"] == 1
    assert stats[1]["level"] == 2
    assert stats[1]["count"] == 1


@pytest.mark.asyncio
async def test_export_json(client, session):
    svc = await create_service(session)
    a = await create_user(session, svc.id)
    b = await create_user(session, svc.id)

    await create_ref(session, a, b, svc, level=1)

    response = client.get(f"/referrals/export/{svc.id}?format=json")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["referrer_id"] == str(a.id)


@pytest.mark.asyncio
async def test_export_csv(client, session):
    svc = await create_service(session)
    a = await create_user(session, svc.id)
    b = await create_user(session, svc.id)

    await create_ref(session, a, b, svc, level=1)

    response = client.get(f"/referrals/export/{svc.id}?format=csv")

    assert response.status_code == 200
    text = response.text

    assert "referrer_id" in text
    assert str(a.id) in text
