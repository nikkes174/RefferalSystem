from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ReferralCodeCreate(BaseModel):
    user_id: UUID
    service_id: UUID
    expires_at: datetime | None = None
    usage_limit: int | None = None


class ReferralCodeRead(BaseModel):
    id: UUID
    code: str
    user_id: UUID
    service_id: UUID
    expires_at: datetime | None
    usage_limit: int | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ReferralCodeUpdate(BaseModel):
    expires_at: datetime | None = None
    usage_limit: int | None = None


class ReferralCodeUsageRead(BaseModel):
    id: UUID
    referral_code_id: UUID
    used_by_user_id: UUID
    used_at: datetime

    class Config:
        from_attributes = True
