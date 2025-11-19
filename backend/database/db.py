# backend/database/db.py

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from contextlib import asynccontextmanager


class Base(DeclarativeBase):
    pass


class Database:
    def __init__(self, url: str | None = None, echo: bool = False):
        self._engine = None
        self._session_factory = None

        if url is not None:
            self.init(url, echo=echo)

    def init(self, url: str, echo: bool = False):
        self._engine = create_async_engine(url, echo=echo)
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @property
    def engine(self):
        return self._engine

    async def create_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def dispose(self):
        await self._engine.dispose()

    @asynccontextmanager
    async def get_session(self):
        real_session: AsyncSession = self._session_factory()
        proxy = SessionProxy(real_session)

        try:
            yield proxy
        finally:
            await real_session.close()
            proxy.closed = True


class SessionProxy:
    def __init__(self, session: AsyncSession):
        self._session = session
        self.closed = False

    # Проксируем атрибуты
    def __getattr__(self, name):
        return getattr(self._session, name)

db = Database()
