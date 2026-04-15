from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.business_unit import BusinessUnitCreate, BusinessUnitRead, BusinessUnitUpdate
from app.services import business_unit_service

router = APIRouter()


@router.get("", response_model=list[BusinessUnitRead])
async def list_business_units(db: AsyncSession = Depends(get_db_session)) -> list[BusinessUnitRead]:
    return await business_unit_service.list_business_units(db)


@router.post("", response_model=BusinessUnitRead, status_code=status.HTTP_201_CREATED)
async def create_business_unit(
    payload: BusinessUnitCreate,
    db: AsyncSession = Depends(get_db_session),
) -> BusinessUnitRead:
    return await business_unit_service.create_business_unit(db, payload)


@router.get("/{business_unit_id}", response_model=BusinessUnitRead)
async def get_business_unit(
    business_unit_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> BusinessUnitRead:
    business_unit = await business_unit_service.get_business_unit_by_id(db, business_unit_id)
    if business_unit is None:
        raise HTTPException(status_code=404, detail="Business unit not found")
    return business_unit


@router.patch("/{business_unit_id}", response_model=BusinessUnitRead)
async def update_business_unit(
    business_unit_id: UUID,
    payload: BusinessUnitUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> BusinessUnitRead:
    business_unit = await business_unit_service.update_business_unit(db, business_unit_id, payload)
    if business_unit is None:
        raise HTTPException(status_code=404, detail="Business unit not found")
    return business_unit
