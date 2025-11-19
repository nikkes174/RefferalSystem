import uuid
import datetime as dt

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from backend.database.db import Base


class ExternalService(AsyncAttrs, Base):
    """ORM-модель внешнего сервиса, подключённого к микросервису."""

    __tablename__ = "external_services"

    # Поля таблицы
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Внутренний UUID внешнего сервиса.",
    )

    service_name: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
        doc="Уникальное имя сервиса.",
    )

    api_key: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        doc="Зашифрованный API key сервиса.",
    )

    webhook_url: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        doc="Webhook URL сервиса (опционально).",
    )

    created_at: Mapped[dt.datetime] = mapped_column(
    DateTime(timezone=True),
    default=lambda: dt.datetime.utcnow(),
    nullable=False,
)

    # ORM-связи
    referral_codes = relationship(
        "ReferralCode",
        back_populates="service",
        cascade="all, delete-orphan",
        doc="Реферальные коды, созданные для этого сервиса.",
    )

    referrals = relationship(
        "Referral",
        back_populates="service",
        doc="Реферальные регистрации, связанные с этим сервисом.",
    )

    users = relationship(
        "UserService",
        back_populates="service",
        cascade="all, delete-orphan",
    )


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("external_services.id"),
        nullable=False,
    )

    url: Mapped[str] = mapped_column(String, nullable=False)

    payload: Mapped[str] = mapped_column(Text, nullable=False)

    response_status: Mapped[int | None] = mapped_column(nullable=True)
    response_body: Mapped[str | None] = mapped_column(Text, nullable=True)

    success: Mapped[bool] = mapped_column(Boolean, default=False)

    attempt: Mapped[int] = mapped_column(default=1)

    created_at: Mapped[dt.datetime] = mapped_column(
    DateTime(timezone=True),
    default=lambda: dt.datetime.utcnow(),
    nullable=False,
)


class ServiceEventLog(Base):
    __tablename__ = "service_event_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("external_services.id"),
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(String(50), nullable=False)

    message: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[dt.datetime] = mapped_column(
    DateTime(timezone=True),
    default=lambda: dt.datetime.utcnow(),
    nullable=False,
)


class ArchivedService(Base):
    __tablename__ = "archived_services"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    original_service_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    service_name: Mapped[str] = mapped_column(String)
    api_key: Mapped[str] = mapped_column(String)
    webhook_url: Mapped[str] = mapped_column(String)

    archived_at: Mapped[dt.datetime] = mapped_column(
        DateTime,
        default=lambda: dt.datetime.utcnow(),
    )


class ArchivedReferralCode(Base):
    __tablename__ = "archived_referral_codes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    original_code_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    service_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    code: Mapped[str] = mapped_column(String)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.utcnow(),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column()


class ArchivedWebhookEvent(Base):
    __tablename__ = "archived_webhook_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    original_event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    service_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    payload: Mapped[str] = mapped_column(Text)
    response_status: Mapped[int | None] = mapped_column()
    success: Mapped[bool] = mapped_column()
    attempt: Mapped[int] = mapped_column()
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.utcnow(),
        nullable=False,
    )
