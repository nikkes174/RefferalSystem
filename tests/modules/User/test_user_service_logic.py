import uuid

import pytest

from backend.User.models import User, UserService
from backend.User.schemas import UserCreate
from backend.User.service import UserServiceLogic


@pytest.mark.asyncio
async def test_register_user_success(session):
    logic = UserServiceLogic()

    data = UserCreate(
        external_user_id="user123",
        service_id=uuid.uuid4(),
    )

    new_user = await logic.register_user(session, data)

    assert new_user.external_user_id == "user123"
    assert new_user.service_id == data.service_id

    # check user saved in DB
    saved_user = await session.get(User, new_user.id)
    assert saved_user is not None

    # check link created
    link = await session.get(UserService, new_user.id)
    assert link is not None
    assert link.service_id == data.service_id


@pytest.mark.asyncio
async def test_register_user_already_registered(session):
    logic = UserServiceLogic()

    service_id = uuid.uuid4()

    # create existing user
    existing = User(
        id=uuid.uuid4(),
        external_user_id="user123",
        service_id=service_id,
    )
    session.add(existing)
    await session.flush()

    # link user <> service
    session.add(
        UserService(
            id=existing.id,
            user_id=existing.id,
            service_id=service_id,
        ),
    )
    await session.flush()

    data = UserCreate(
        external_user_id="user123",
        service_id=service_id,
    )

    with pytest.raises(ValueError):
        await logic.register_user(session, data)


@pytest.mark.asyncio
async def test_get_user_services(session):
    logic = UserServiceLogic()

    user_id = uuid.uuid4()

    s1 = UserService(id=uuid.uuid4(), user_id=user_id, service_id=uuid.uuid4())
    s2 = UserService(id=uuid.uuid4(), user_id=user_id, service_id=uuid.uuid4())

    session.add_all([s1, s2])
    await session.flush()

    result = await logic.get_user_services(session, user_id)

    assert len(result) == 2
    assert set(result) == {s1.service_id, s2.service_id}


@pytest.mark.asyncio
async def test_get_users_of_service(session):
    logic = UserServiceLogic()

    service_id = uuid.uuid4()

    u1 = UserService(
        id=uuid.uuid4(), user_id=uuid.uuid4(), service_id=service_id
    )
    u2 = UserService(
        id=uuid.uuid4(), user_id=uuid.uuid4(), service_id=service_id
    )

    session.add_all([u1, u2])
    await session.flush()

    result = await logic.get_users_of_service(session, service_id)

    assert len(result) == 2
    assert set(result) == {u1.user_id, u2.user_id}
