from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval import Approval
from app.schemas.approval import ApprovalCreate, ApprovalDecision


async def list_approvals(
    db: AsyncSession,
    *,
    status_filter: str | None = None,
    project_id: UUID | None = None,
) -> list[Approval]:
    query: Select[tuple[Approval]] = select(Approval)
    if status_filter:
        query = query.where(Approval.status == status_filter)
    if project_id:
        query = query.where(Approval.project_id == project_id)
    query = query.order_by(Approval.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_approval(db: AsyncSession, payload: ApprovalCreate) -> Approval:
    approval = Approval(**payload.model_dump())
    db.add(approval)
    await db.commit()
    await db.refresh(approval)
    return approval


async def get_approval_by_id(db: AsyncSession, approval_id: UUID) -> Approval | None:
    return await db.get(Approval, approval_id)


async def approve_approval(
    db: AsyncSession,
    approval_id: UUID,
    payload: ApprovalDecision,
) -> Approval | None:
    return await _decide_approval(db, approval_id, "approved", payload.decided_by)


async def reject_approval(
    db: AsyncSession,
    approval_id: UUID,
    payload: ApprovalDecision,
) -> Approval | None:
    return await _decide_approval(db, approval_id, "rejected", payload.decided_by)


async def _decide_approval(
    db: AsyncSession,
    approval_id: UUID,
    decision: str,
    decided_by: str,
) -> Approval | None:
    approval = await db.get(Approval, approval_id)
    if approval is None:
        return None

    approval.status = decision
    approval.decision = decision
    approval.decided_by = decided_by
    approval.decided_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(approval)
    return approval
