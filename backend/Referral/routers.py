import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

import backend.database.db as db_module
from backend.Referral.schemas import (
    ReferralCreate,
    ReferralLevelUpdate,
    ReferralRead,
    ReferralStats,
)
from backend.Referral.service import ReferralService

router = APIRouter(prefix="/referrals", tags=["Referrals"])
referral_service = ReferralService()


async def get_session():
    async with db_module.db.get_session() as session:
        yield session


@router.post("/", response_model=ReferralRead)
async def register_referral(
    data: ReferralCreate,
    session: AsyncSession = Depends(get_session),
):
    try:
        ref = await referral_service.register_referral(session, data)
        return ref
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}/{service_id}", response_model=list[ReferralRead])
async def get_user_referrals(
    user_id: UUID,
    service_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    return await referral_service.get_user_referrals(
        session, user_id, service_id
    )


@router.get("/chain/{user_id}/{service_id}")
async def get_parent_chain(
    user_id: UUID,
    service_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    return await referral_service.get_parent_chain(
        session, user_id, service_id
    )


@router.get("/top/{service_id}")
async def get_top_referrers(
    service_id: UUID,
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
):
    return await referral_service.get_top_referrers(session, service_id, limit)


@router.get("/stats/{service_id}", response_model=list[ReferralStats])
async def get_referral_stats(
    service_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    return await referral_service.get_stats(session, service_id)


@router.get("/export/{service_id}")
async def export_referrals(
    service_id: UUID,
    format: str = Query("json", enum=["json", "csv"]),
    session: AsyncSession = Depends(get_session),
):
    raw_data = await referral_service.export_referrals(
        session, service_id, format
    )

    if format == "json":
        return JSONResponse(content=json.loads(raw_data))

    return PlainTextResponse(raw_data, media_type="text/csv")


@router.patch("/{referral_id}/level", response_model=ReferralRead)
async def update_referral_level(
    referral_id: UUID,
    data: ReferralLevelUpdate,
    session: AsyncSession = Depends(get_session),
):
    try:
        updated = await referral_service.force_update_level(
            session,
            referral_id,
            data.level,
        )
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
