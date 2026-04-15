from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business_unit import BusinessUnit
from app.schemas.business_unit import BusinessUnitCreate, BusinessUnitUpdate


async def list_business_units(db: AsyncSession) -> list[BusinessUnit]:
    result = await db.execute(select(BusinessUnit).order_by(BusinessUnit.name.asc()))
    return list(result.scalars().all())


async def create_business_unit(db: AsyncSession, payload: BusinessUnitCreate) -> BusinessUnit:
    business_unit = BusinessUnit(**payload.model_dump())
    db.add(business_unit)
    await db.commit()
    await db.refresh(business_unit)
    return business_unit


async def get_business_unit_by_id(db: AsyncSession, business_unit_id: UUID) -> BusinessUnit | None:
    return await db.get(BusinessUnit, business_unit_id)


async def update_business_unit(
    db: AsyncSession,
    business_unit_id: UUID,
    payload: BusinessUnitUpdate,
) -> BusinessUnit | None:
    business_unit = await db.get(BusinessUnit, business_unit_id)
    if business_unit is None:
        return None

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(business_unit, field, value)

    await db.commit()
    await db.refresh(business_unit)
    return business_unit
