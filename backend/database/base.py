from typing import Generic, List, Type, TypeVar, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from backend.database.db import Base

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, session: AsyncSession, id) -> Optional[ModelType]:
        return await session.get(self.model, id)

    async def get_all(self, session: AsyncSession):
        result = await session.execute(select(self.model))
        return result.scalars().all()

    async def create(self, session: AsyncSession, obj: ModelType) -> ModelType:
        session.add(obj)
        await session.flush()
        return obj

    async def delete(self, session, obj):
        await session.delete(obj)
        await session.commit()
