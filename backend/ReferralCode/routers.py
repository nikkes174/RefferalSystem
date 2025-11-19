from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import backend.database.db as db_module

from backend.ReferralCode.schemas import (
    ReferralCodeCreate,
    ReferralCodeRead,
    ReferralCodeUpdate,
    ReferralCodeUsageRead,
)
from backend.ReferralCode.service import ReferralCodeService

router = APIRouter(prefix="/referral-codes", tags=["Referral Codes"])

service = ReferralCodeService()


async def get_session():
    async with db_module.db.get_session() as session:
        yield session


@router.post("/", response_model=ReferralCodeRead)
async def create_code(
    data: ReferralCodeCreate,
    session: AsyncSession = Depends(get_session),
):
    return await service.create_code(session, data)


@router.get("/{code}", response_model=ReferralCodeRead)
async def validate_code(
    code: str,
    session: AsyncSession = Depends(get_session),
):
    try:
        return await service.validate_code(session, code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{code_id}", response_model=ReferralCodeRead)
async def update_limits(
    code_id: UUID,
    data: ReferralCodeUpdate,
    session: AsyncSession = Depends(get_session),
):
    return await service.update_limits(session, code_id, data)


@router.post("/{code_id}/deactivate")
async def deactivate_code(
    code_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    return await service.deactivate_code(session, code_id)


@router.get("/service/{service_id}", response_model=list[ReferralCodeRead])
async def get_codes_by_service(
    service_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    return await service.get_codes_by_service(session, service_id)


@router.get("/inactive/{service_id}", response_model=list[ReferralCodeRead])
async def get_inactive_codes(
    service_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    return await service.get_inactive_codes(session, service_id)


@router.get("/history/{code_id}", response_model=list[ReferralCodeUsageRead])
async def get_referral_code_history(
    code_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    return await service.get_usage_history(session, code_id)


@router.delete("/history/{code_id}")
async def clear_referral_code_history(
    code_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    await service.clear_usage(session, code_id)
    return {"status": "ok"}
