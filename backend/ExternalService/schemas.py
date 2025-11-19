from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class ExternalServiceBase(BaseModel):
    service_name: str = Field(..., description="Уникальное имя сервиса")
    webhook_url: HttpUrl | None = Field(
        None,
        description="Webhook URL сервиса",
    )


class ExternalServiceCreate(ExternalServiceBase):
    api_key: str = Field(
        ...,
        description="Секретный API Key (будет зашифрован)",
    )


class ExternalServiceUpdate(BaseModel):
    webhook_url: str | None = None


class ExternalServiceRead(ExternalServiceBase):
    id: UUID = Field(..., description="ID сервиса")
    created_at: datetime = Field(...)

    class Config:
        from_attributes = True


class ServiceEventLogRead(BaseModel):
    id: UUID
    service_id: UUID
    event_type: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True
