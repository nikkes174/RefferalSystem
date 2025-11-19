from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.User.models import User, UserService
from backend.User.schemas import UserCreate


class UserServiceLogic:

    # ------------------------------------------------------
    # 1. Создание пользователя
    # ------------------------------------------------------
    async def register_user(self, session: AsyncSession, data: UserCreate) -> User:

        # Проверяем наличие пользователя
        user = await session.scalar(
            select(User).where(
                User.external_user_id == data.external_user_id,
                User.service_id == data.service_id,
            )
        )

        if user:
            raise ValueError("User already exists")

        # Создаём пользователя
        user = User(
            external_user_id=data.external_user_id,
            service_id=data.service_id,
        )
        session.add(user)
        await session.flush()

        # Привязываем в user_services
        link = UserService(
            user_id=user.id,
            service_id=data.service_id,
        )
        session.add(link)
        await session.flush()

        return user


    async def get_user_services(self, session: AsyncSession, user_id: UUID):
        result = await session.execute(
            select(UserService).where(UserService.user_id == user_id)
        )
        return result.scalars().all()


    async def get_users_of_service(self, session: AsyncSession, service_id: UUID):
        result = await session.execute(
            select(UserService).where(UserService.service_id == service_id)
        )
        return result.scalars().all()
