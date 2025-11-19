import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.database.base import Base
from backend.ExternalService.models import ExternalService
from backend.User.models import User
from main import app


@pytest.fixture(scope="function")
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


@pytest.mark.asyncio
async def test_register_referral(client, session):
    svc = await create_service(session)
    referrer = await create_user(session, svc.id)
    referred = await create_user(session, svc.id)

    payload = {
        "referrer_id": str(referrer.id),
        "referred_id": str(referred.id),
        "service_id": str(svc.id),
        "referral_code_id": None,
    }

    response = client.post("/referrals/", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["referrer_id"] == str(referrer.id)
    assert data["referred_id"] == str(referred.id)
    assert data["level"] == 1


@pytest.mark.asyncio
async def test_cycle_block(client, session):
    svc = await create_service(session)
    a = await create_user(session, svc.id)
    b = await create_user(session, svc.id)

    client.post(
        "/referrals/",
        json={
            "referrer_id": str(a.id),
            "referred_id": str(b.id),
            "service_id": str(svc.id),
            "referral_code_id": None,
        },
    )

    response = client.post(
        "/referrals/",
        json={
            "referrer_id": str(b.id),
            "referred_id": str(a.id),
            "service_id": str(svc.id),
            "referral_code_id": None,
        },
    )

    assert response.status_code == 400
    assert "cycle" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_user_referrals(client, session):
    svc = await create_service(session)
    a = await create_user(session, svc.id)
    b = await create_user(session, svc.id)

    client.post(
        "/referrals/",
        json={
            "referrer_id": str(a.id),
            "referred_id": str(b.id),
            "service_id": str(svc.id),
            "referral_code_id": None,
        },
    )

    response = client.get(f"/referrals/{a.id}/{svc.id}")

    assert response.status_code == 200
    arr = response.json()
    assert len(arr) == 1
    assert arr[0]["referred_id"] == str(b.id)


@pytest.mark.asyncio
async def test_get_parent_chain(client, session):
    svc = await create_service(session)
    a = await create_user(session, svc.id)
    b = await create_user(session, svc.id)
    c = await create_user(session, svc.id)

    # A → B
    client.post(
        "/referrals/",
        json={
            "referrer_id": str(a.id),
            "referred_id": str(b.id),
            "service_id": str(svc.id),
            "referral_code_id": None,
        },
    )

    # B → C
    client.post(
        "/referrals/",
        json={
            "referrer_id": str(b.id),
            "referred_id": str(c.id),
            "service_id": str(svc.id),
            "referral_code_id": None,
        },
    )

    response = client.get(f"/referrals/chain/{c.id}/{svc.id}")

    assert response.status_code == 200
    chain = response.json()
    assert len(chain) == 1
    assert chain[0]["referrer_id"] == str(b.id)


@pytest.mark.asyncio
async def test_get_top_referrers(client, session):
    svc = await create_service(session)

    a = await create_user(session, svc.id)
    b = await create_user(session, svc.id)
    c = await create_user(session, svc.id)

    client.post(
        "/referrals/",
        json={
            "referrer_id": str(a.id),
            "referred_id": str(b.id),
            "service_id": str(svc.id),
            "referral_code_id": None,
        },
    )

    client.post(
        "/referrals/",
        json={
            "referrer_id": str(a.id),
            "referred_id": str(c.id),
            "service_id": str(svc.id),
            "referral_code_id": None,
        },
    )

    response = client.get(f"/referrals/top/{svc.id}?limit=1")

    assert response.status_code == 200
    top = response.json()
    assert top[0]["referrer_id"] == str(a.id)
    assert top[0]["count"] == 2
