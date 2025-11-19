import uuid
import datetime as dt

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from backend.database.db import Base



class ReferralCode(AsyncAttrs, Base):
    """ORM-модель реферального кода."""

    __tablename__ = "referral_codes"

    # Поля таблицы
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="UUID реферального кода.",
    )

    code: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="Уникальный текстовый код (например: ABC123-XYZ).",
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        doc="ID пользователя-владельца кода.",
    )

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("external_services.id"),
        nullable=False,
        doc="ID внешнего сервиса, для которого действует код.",
    )

    expires_at: Mapped[dt.datetime | None] = mapped_column(

        DateTime(timezone=True),
        nullable=True,
        doc="Срок действия кода (None = бессрочно).",
    )

    usage_limit: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Максимальное количество использований (None = без ограничений).",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        doc="Активен ли код.",
    )

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: dt.datetime.utcnow(),
    )

    __table_args__ = (
        UniqueConstraint(
            "code",
            "service_id",
            name="uq_referral_code_service",
        ),
    )

    # ORM-связи
    user = relationship(
        "User",
        back_populates="referral_codes",
        doc="Пользователь, которому принадлежит код.",
    )

    service = relationship(
        "ExternalService",
        back_populates="referral_codes",
        doc="Сервис, в рамках которого действует код.",
    )

    referrals = relationship(
        "Referral",
        back_populates="referral_code",
        doc="Список регистраций, совершённых с использованием этого кода.",
    )
    usage_records = relationship(
        "ReferralCodeUsage",
        back_populates="referral_code",
        cascade="all, delete-orphan",
    )


class ReferralCodeUsage(Base):
    __tablename__ = "referral_code_usage"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    referral_code_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("referral_codes.id"),
        nullable=False,
        index=True,
    )

    used_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    used_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.utcnow(),
        nullable=False,
    )

    referral_code = relationship(
        "ReferralCode", back_populates="usage_records"
    )
