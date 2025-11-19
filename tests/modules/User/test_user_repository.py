import uuid

import pytest

from backend.User.models import User
from backend.User.repository import UserRepository


@pytest.mark.asyncio
async def test_create_user(session):
    repo = UserRepository()

    user = User(
        id=uuid.uuid4(),
        external_user_id="test_123",
        service_id=uuid.uuid4(),
    )

    created = await repo.create_user(session, user)

    assert created.id == user.id
    assert created.external_user_id == "test_123"


@pytest.mark.asyncio
async def test_get_by_external_id(session):
    repo = UserRepository()

    user = User(
        id=uuid.uuid4(),
        external_user_id="external_1",
        service_id=uuid.uuid4(),
    )
    session.add(user)
    await session.flush()

    found = await repo.get_by_external_id(session, "external_1")

    assert found is not None
    assert found.external_user_id == "external_1"


@pytest.mark.asyncio
async def test_get_by_external_id_not_found(session):
    repo = UserRepository()

    found = await repo.get_by_external_id(session, "unknown")

    assert found is None


@pytest.mark.asyncio
async def test_get_by_id(session):
    repo = UserRepository()

    user = User(
        id=uuid.uuid4(),
        external_user_id="user_x",
        service_id=uuid.uuid4(),
    )
    session.add(user)
    await session.flush()

    found = await repo.get_by_id(session, user.id)

    assert found is not None
    assert found.id == user.id


@pytest.mark.asyncio
async def test_get_by_id_not_found(session):
    repo = UserRepository()

    found = await repo.get_by_id(session, uuid.uuid4())

    assert found is None
