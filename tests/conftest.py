import pytest
import asyncio

# Загружаем ВСЕ модели (важно!)
import backend.ExternalService.models
import backend.Referral.models
import backend.ReferralCode.models
import backend.User.models

from httpx import AsyncClient, ASGITransport

from fastapi import FastAPI
from backend.database.db import db
from backend.database.db import Base

from main import app as real_app


# -----------------------------
#  Убираем все middleware
# -----------------------------
def strip_middlewares(app: FastAPI) -> FastAPI:
    new_app = FastAPI(title=app.title)
    new_app.router.routes = app.router.routes
    return new_app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    TEST_DB = "sqlite+aiosqlite:///./test.db"
    db.init(TEST_DB)

    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await db.dispose()


@pytest.fixture
async def session():
    async with db.get_session() as s:
        yield s


@pytest.fixture
async def async_session():
    async with db.get_session() as s:
        yield s


# -----------------------------
#  HTTP-клиент БЕЗ middleware
# -----------------------------
@pytest.fixture
async def client():
    test_app = strip_middlewares(real_app)

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
