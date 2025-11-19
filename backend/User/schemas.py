import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    external_user_id: str = Field(
        ...,
        description="ID пользователя из внешнего сервиса",
    )
    service_id: uuid.UUID = Field(
        ...,
        description="ID внешнего сервиса",
    )


class UserCreate(UserBase):
    """Данные для создания пользователя"""


class UserRead(UserBase):
    id: uuid.UUID = Field(
        ...,
        description="Внутренний UUID пользователя в микросервисе",
    )
    created_at: datetime = Field(..., description="Дата и время создания")

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    external_user_id: str | None = None
    service_id: uuid.UUID | None = None

    class Config:
        from_attributes = True

class UserServiceRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    service_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
