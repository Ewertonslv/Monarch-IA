from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.approval import ApprovalCreate, ApprovalDecision, ApprovalRead
from app.services import approval_service

router = APIRouter()


@router.get("", response_model=list[ApprovalRead])
async def list_approvals(
    status_filter: str | None = Query(default=None, alias="status"),
    project_id: UUID | None = None,
    db: AsyncSession = Depends(get_db_session),
) -> list[ApprovalRead]:
    return await approval_service.list_approvals(
        db,
        status_filter=status_filter,
        project_id=project_id,
    )


@router.post("", response_model=ApprovalRead, status_code=status.HTTP_201_CREATED)
async def create_approval(
    payload: ApprovalCreate,
    db: AsyncSession = Depends(get_db_session),
) -> ApprovalRead:
    return await approval_service.create_approval(db, payload)


@router.get("/{approval_id}", response_model=ApprovalRead)
async def get_approval(approval_id: UUID, db: AsyncSession = Depends(get_db_session)) -> ApprovalRead:
    approval = await approval_service.get_approval_by_id(db, approval_id)
    if approval is None:
        raise HTTPException(status_code=404, detail="Approval not found")
    return approval


@router.post("/{approval_id}/approve", response_model=ApprovalRead)
async def approve_approval(
    approval_id: UUID,
    payload: ApprovalDecision,
    db: AsyncSession = Depends(get_db_session),
) -> ApprovalRead:
    approval = await approval_service.approve_approval(db, approval_id, payload)
    if approval is None:
        raise HTTPException(status_code=404, detail="Approval not found")
    return approval


@router.post("/{approval_id}/reject", response_model=ApprovalRead)
async def reject_approval(
    approval_id: UUID,
    payload: ApprovalDecision,
    db: AsyncSession = Depends(get_db_session),
) -> ApprovalRead:
    approval = await approval_service.reject_approval(db, approval_id, payload)
    if approval is None:
        raise HTTPException(status_code=404, detail="Approval not found")
    return approval
