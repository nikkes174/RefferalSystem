import uuid

import pytest
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.base import Base, BaseRepository


class TestModel(Base):
    __tablename__ = "test_model"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)


@pytest.fixture
async def test_repo():
    return BaseRepository(TestModel)


async def test_create_and_get(async_session: AsyncSession, test_repo):
    obj = TestModel(name="test")
    created = await test_repo.create(async_session, obj)

    assert created.id is not None
    assert created.name == "test"

    fetched = await test_repo.get(async_session, created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "test"


async def test_get_all(async_session: AsyncSession, test_repo):
    obj1 = TestModel(name="A")
    obj2 = TestModel(name="B")

    await test_repo.create(async_session, obj1)
    await test_repo.create(async_session, obj2)

    all_items = await test_repo.get_all(async_session)
    assert len(all_items) == 2
    assert {i.name for i in all_items} == {"A", "B"}


async def test_delete(async_session: AsyncSession, test_repo):
    obj = TestModel(name="to-delete")
    await test_repo.create(async_session, obj)

    await test_repo.delete(async_session, obj)
    fetched = await test_repo.get(async_session, obj.id)

    assert fetched is None
