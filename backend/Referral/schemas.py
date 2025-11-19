from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ReferralCreate(BaseModel):
    referrer_id: UUID
    referred_id: UUID
    service_id: UUID
    referral_code_id: UUID | None = None


class ReferralRead(BaseModel):
    id: UUID
    referrer_id: UUID
    referred_id: UUID
    service_id: UUID
    level: int
    registered_at: datetime

    class Config:
        from_attributes = True


class ReferralStats(BaseModel):
    level: int
    count: int


class ReferralLevelUpdate(BaseModel):
    level: int
