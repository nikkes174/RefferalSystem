import uuid

import pytest
from httpx import AsyncClient

from backend.User.models import User, UserService


@pytest.mark.asyncio
async def test_register_user_api(session, client: AsyncClient):
    payload = {
        "external_user_id": "user123",
        "service_id": str(uuid.uuid4()),
    }

    response = await client.post("/users/", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["external_user_id"] == "user123"
    assert "id" in data

    # проверяем, что запись реально в БД
    saved = await session.get(User, uuid.UUID(data["id"]))
    assert saved is not None


@pytest.mark.asyncio
async def test_register_user_already_exists_api(session, client: AsyncClient):
    service_id = uuid.uuid4()

    # создания исходного пользователя
    user = User(
        id=uuid.uuid4(),
        external_user_id="existing",
        service_id=service_id,
    )
    session.add(user)
    await session.flush()

    # создание записи в UserService
    us = UserService(
        id=uuid.uuid4(),
        user_id=user.id,
        service_id=service_id,
    )
    session.add(us)
    await session.flush()

    payload = {
        "external_user_id": "existing",
        "service_id": str(service_id),
    }

    response = await client.post("/users/", json=payload)

    assert response.status_code == 400  # ValueError → HTTP 400
    assert "Пользователь уже регистрировался" in response.text


@pytest.mark.asyncio
async def test_get_user_services_api(session, client: AsyncClient):
    user_id = uuid.uuid4()

    s1 = UserService(id=uuid.uuid4(), user_id=user_id, service_id=uuid.uuid4())
    s2 = UserService(id=uuid.uuid4(), user_id=user_id, service_id=uuid.uuid4())

    session.add_all([s1, s2])
    await session.flush()

    response = await client.get(f"/users/{user_id}/services")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert set(data) == {str(s1.service_id), str(s2.service_id)}


@pytest.mark.asyncio
async def test_get_users_of_service_api(session, client: AsyncClient):
    service_id = uuid.uuid4()

    u1 = UserService(
        id=uuid.uuid4(), user_id=uuid.uuid4(), service_id=service_id
    )
    u2 = UserService(
        id=uuid.uuid4(), user_id=uuid.uuid4(), service_id=service_id
    )

    session.add_all([u1, u2])
    await session.flush()

    response = await client.get(f"/users/service/{service_id}/users")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert set(data) == {str(u1.user_id), str(u2.user_id)}
