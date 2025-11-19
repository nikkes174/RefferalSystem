from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import backend.database.db as db_module

from backend.User.schemas import (
    UserCreate,
    UserRead,
    UserServiceRead,
)
from backend.User.service import UserServiceLogic

router = APIRouter(prefix="/users", tags=["Users"])

logic = UserServiceLogic()


async def get_session():
    async with db_module.db.get_session() as session:
        yield session


# -----------------------------
# POST /users/  — создание пользователя
# -----------------------------
@router.post("/", response_model=UserRead)
async def register_user(
    data: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    try:
        user = await logic.register_user(session, data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------
# GET /users/{user_id}/services — список сервисов пользователя
# -----------------------------
@router.get("/{user_id}/services", response_model=list[UserServiceRead])
async def get_user_services(
    user_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    services = await logic.get_user_services(session, user_id)
    return services


# -----------------------------
# GET /users/service/{service_id}/users — пользователи сервиса
# -----------------------------
@router.get("/service/{service_id}/users", response_model=list[UserServiceRead])
async def get_users_of_service(
    service_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    users = await logic.get_users_of_service(session, service_id)
    return users
