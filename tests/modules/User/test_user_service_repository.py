import uuid

import pytest

from backend.User.models import User, UserService
from backend.User.repository import UserServiceRepository


@pytest.mark.asyncio
async def test_add_user_to_service(session):
    repo = UserServiceRepository()

    user_id = uuid.uuid4()
    service_id = uuid.uuid4()

    link = await repo.add_user_to_service(
        session=session,
        user_id=user_id,
        service_id=service_id,
    )

    assert link.user_id == user_id
    assert link.service_id == service_id

    result = await session.get(UserService, link.id)
    assert result is not None


@pytest.mark.asyncio
async def test_get_services_by_user_id(session):
    repo = UserServiceRepository()

    user_id = uuid.uuid4()

    s1 = UserService(id=uuid.uuid4(), user_id=user_id, service_id=uuid.uuid4())
    s2 = UserService(id=uuid.uuid4(), user_id=user_id, service_id=uuid.uuid4())

    session.add_all([s1, s2])
    await session.flush()

    services = await repo.get_services_by_user_id(session, user_id)

    assert len(services) == 2
    assert {s.service_id for s in services} == {s1.service_id, s2.service_id}


@pytest.mark.asyncio
async def test_user_exists_in_service(session):
    repo = UserServiceRepository()

    service_id = uuid.uuid4()

    user = User(
        id=uuid.uuid4(),
        external_user_id="ext_x",
        service_id=service_id,
    )
    session.add(user)
    await session.flush()

    found = await repo.user_exists_in_service(
        session=session,
        external_user_id="ext_x",
        service_id=service_id,
    )

    assert found is not None
    assert found.external_user_id == "ext_x"


@pytest.mark.asyncio
async def test_user_exists_in_service_not_found(session):
    repo = UserServiceRepository()

    found = await repo.user_exists_in_service(
        session=session,
        external_user_id="unknown",
        service_id=uuid.uuid4(),
    )

    assert found is None


@pytest.mark.asyncio
async def test_get_users_by_service_id(session):
    repo = UserServiceRepository()

    service_id = uuid.uuid4()

    u1 = UserService(
        id=uuid.uuid4(), user_id=uuid.uuid4(), service_id=service_id
    )
    u2 = UserService(
        id=uuid.uuid4(), user_id=uuid.uuid4(), service_id=service_id
    )

    session.add_all([u1, u2])
    await session.flush()

    result = await repo.get_users_by_service_id(session, service_id)

    assert len(result) == 2
    assert {r.user_id for r in result} == {u1.user_id, u2.user_id}
