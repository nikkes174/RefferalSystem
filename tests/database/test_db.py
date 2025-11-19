import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from backend.database.db import Database


@pytest.fixture
def test_db():
    return Database("sqlite+aiosqlite:///:memory:", echo=False)


async def test_engine_created(test_db):
    assert isinstance(test_db.engine, AsyncEngine)


async def test_get_session_returns_session(test_db):
    async with test_db.get_session() as session:
        assert isinstance(session, AsyncSession)
        assert session.is_active


async def test_session_closes_after_exit(test_db):
    async with test_db.get_session() as session:
        assert not session.closed
    assert session.closed


async def test_engine_dispose(test_db):
    await test_db.dispose()
    assert test_db.engine.sync_engine.pool.dispose is not None
