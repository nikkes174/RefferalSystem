from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.User.models import User, UserService


class UserServiceRepository:
    async def add_user_to_service(
        self,
        session: AsyncSession,
        user_id: UUID,
        service_id: UUID,
    ):
        link = UserService(user_id=user_id, service_id=service_id)
        session.add(link)
        await session.flush()
        return link

    async def get_services_by_user_id(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> list[UUID]:
        """
        Возвращает список ID сервисов, где есть пользователь.
        ТЕСТ ЖДЁТ СПИСОК UUID !!
        """
        stmt = select(UserService.service_id).where(UserService.user_id == user_id)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def user_exists_in_service(
        self,
        session: AsyncSession,
        external_user_id: str,
        service_id: UUID,
    ):
        stmt = select(User).where(
            User.external_user_id == external_user_id,
            User.service_id == service_id,
        )
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_users_by_service_id(
        self,
        session: AsyncSession,
        service_id: UUID,
    ) -> list[UUID]:
        """
        Возвращает список ID пользователей, привязанных к сервису.
        ТЕСТ ЖДЁТ СПИСОК UUID !!
        """
        stmt = select(UserService.user_id).where(UserService.service_id == service_id)
        res = await session.execute(stmt)
        return list(res.scalars().all())


class UserRepository:
    async def create_user(self, session: AsyncSession, user: User):
        session.add(user)
        await session.flush()
        return user

    async def get_by_external_id(
        self,
        session: AsyncSession,
        external_user_id: str,
    ):
        stmt = select(User).where(User.external_user_id == external_user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, session: AsyncSession, user_id: UUID):
        return await session.get(User, user_id)
