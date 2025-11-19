import uuid
import datetime as dt
from sqlalchemy.sql import func
from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from backend.database.db import Base


class Referral(AsyncAttrs, Base):
    """ORM-модель реферальной связи."""

    __tablename__ = "referrals"

    # Поля таблицы
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="UUID записи реферальной связи.",
    )

    referrer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        doc="ID пользователя, который пригласил.",
    )

    referred_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        doc="ID пользователя, который был приглашён.",
    )

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("external_services.id"),
        nullable=False,
        doc="ID внешнего сервиса, в рамках которого произошла регистрация.",
    )

    referral_code_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("referral_codes.id"),
        nullable=True,
        doc="ID использованного реферального кода (если был).",
    )

    level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Уровень реферала: 1 — прямой, 2 — реферал реферала и т.д.",
    )

    registered_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # ORM-связи
    referrer = relationship(
        "User",
        back_populates="referrals_sent",
        foreign_keys=[referrer_id],
        doc="Пользователь, который пригласил.",
    )

    referred = relationship(
        "User",
        back_populates="referrals_received",
        foreign_keys=[referred_id],
        doc="Пользователь, который был приглашён.",
    )

    service = relationship(
        "ExternalService",
        back_populates="referrals",
        doc="Сервис, в котором произошла регистрация.",
    )

    referral_code = relationship(
        "ReferralCode",
        back_populates="referrals",
        doc="Реферальный код, использованный при регистрации (если был).",
    )
