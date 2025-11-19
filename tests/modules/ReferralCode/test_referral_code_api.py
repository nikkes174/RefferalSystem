import uuid
from datetime import datetime, timedelta

from httpx import AsyncClient

from backend.ReferralCode.models import ReferralCode


async def test_create_code(async_client: AsyncClient, async_session):
    payload = {
        "user_id": str(uuid.uuid4()),
        "service_id": str(uuid.uuid4()),
        "expires_at": None,
        "usage_limit": None,
    }

    response = await async_client.post("/referral-codes/", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert "code" in data
    assert data["user_id"] == payload["user_id"]
    assert data["service_id"] == payload["service_id"]


async def test_validate_code(async_client: AsyncClient, async_session):
    # Создаём код вручную
    code = ReferralCode(
        id=uuid.uuid4(),
        code="TEST123-ABC",
        user_id=uuid.uuid4(),
        service_id=uuid.uuid4(),
        expires_at=None,
        usage_limit=None,
        is_active=True,
    )
    async_session.add(code)
    await async_session.commit()

    response = await async_client.get(f"/referral-codes/{code.code}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "TEST123-ABC"


async def test_validate_code_expired(async_client: AsyncClient, async_session):
    code = ReferralCode(
        id=uuid.uuid4(),
        code="EXPIRED-111",
        user_id=uuid.uuid4(),
        service_id=uuid.uuid4(),
        expires_at=datetime.utcnow() - timedelta(days=1),
        usage_limit=None,
        is_active=True,
    )
    async_session.add(code)
    await async_session.commit()

    response = await async_client.get("/referral-codes/EXPIRED-111")

    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()


async def test_update_limits(async_client: AsyncClient, async_session):
    code = ReferralCode(
        id=uuid.uuid4(),
        code="LIMIT-TEST",
        user_id=uuid.uuid4(),
        service_id=uuid.uuid4(),
        expires_at=None,
        usage_limit=None,
        is_active=True,
    )
    async_session.add(code)
    await async_session.commit()

    payload = {
        "expires_at": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "usage_limit": 5,
    }

    response = await async_client.patch(
        f"/referral-codes/{code.id}", json=payload
    )

    assert response.status_code == 200
    data = response.json()
    assert data["usage_limit"] == 5


async def test_deactivate_code(async_client: AsyncClient, async_session):
    code = ReferralCode(
        id=uuid.uuid4(),
        code="DEACT-TEST",
        user_id=uuid.uuid4(),
        service_id=uuid.uuid4(),
        is_active=True,
    )
    async_session.add(code)
    await async_session.commit()

    response = await async_client.post(f"/referral-codes/{code.id}/deactivate")

    assert response.status_code == 200
    updated = await async_session.get(ReferralCode, code.id)
    assert updated.is_active is False


async def test_get_codes_by_service(async_client: AsyncClient, async_session):
    service_id = uuid.uuid4()

    codes = [
        ReferralCode(
            id=uuid.uuid4(),
            code=f"SERV-{i}",
            user_id=uuid.uuid4(),
            service_id=service_id,
            is_active=True,
        )
        for i in range(3)
    ]
    async_session.add_all(codes)
    await async_session.commit()

    response = await async_client.get(f"/referral-codes/service/{service_id}")

    assert response.status_code == 200
    assert len(response.json()) == 3


async def test_get_inactive_codes(async_client: AsyncClient, async_session):
    service_id = uuid.uuid4()

    codes = [
        ReferralCode(
            id=uuid.uuid4(),
            code=f"INACTIVE-{i}",
            user_id=uuid.uuid4(),
            service_id=service_id,
            is_active=False,
        )
        for i in range(2)
    ]
    active_code = ReferralCode(
        id=uuid.uuid4(),
        code="ACTIVE-1",
        user_id=uuid.uuid4(),
        service_id=service_id,
        is_active=True,
    )

    async_session.add_all(codes + [active_code])
    await async_session.commit()

    response = await async_client.get(f"/referral-codes/inactive/{service_id}")

    assert response.status_code == 200
    assert len(response.json()) == 2
