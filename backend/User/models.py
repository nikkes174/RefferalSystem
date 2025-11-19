from __future__ import annotations

import datetime
import uuid

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from backend.database.db import Base



class User(AsyncAttrs, Base):
    """ORM-модель пользователя микросервиса."""

    __tablename__ = "users"

    # Поля таблицы
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Внутренний UUID пользователя в микросервисе.",
    )

    external_user_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
        index=True,
        doc="ID пользователя из внешнего сервиса.",
    )

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("external_services.id"),
        nullable=False,
        doc="ID внешнего сервиса, к которому относится пользователь.",
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        nullable=False,
        doc="Дата создания пользователя в системе.",
    )

    # ORM-связи
    referral_codes = relationship(
        "ReferralCode",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="Реферальные коды, принадлежащие пользователю.",
    )

    referrals_sent = relationship(
        "Referral",
        back_populates="referrer",
        foreign_keys="Referral.referrer_id",
        doc="Список записей, кого пригласил этот пользователь.",
    )

    referrals_received = relationship(
        "Referral",
        back_populates="referred",
        foreign_keys="Referral.referred_id",
        doc="Список записей, где данный пользователь был приглашён.",
    )

    services = relationship(
        "UserService",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserService(AsyncAttrs, Base):
    __tablename__ = "user_services"

    # Поля таблицы
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="ID записи связи пользователя и сервиса.",
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        doc="ID пользователя.",
    )

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("external_services.id"),
        nullable=False,
        doc="ID сервиса, в котором зарегистрирован пользователь.",
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        nullable=False,
        doc="Дата привязки пользователя к сервису.",
    )

    # ORM-связи
    user = relationship("User", back_populates="services")
    service = relationship("ExternalService", back_populates="users")
