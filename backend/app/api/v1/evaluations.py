"""
Evaluation Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
import uuid

from app.dependencies import get_db
from app.core.auth import get_current_active_user, require_permission, Permission
from app.models.user import User
from app.models.evaluation import Evaluation, EvaluationStatus
from app.models.bid import Bid
from app.schemas.evaluation import (
    EvaluationCreate,
    EvaluationResponse,
    EvaluationListResponse,
    EvaluationSummary,
    EvaluationConfig,
    BidAdd,
)

router = APIRouter()


def generate_reference_id() -> str:
    """Generate a unique reference ID"""
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    unique = str(uuid.uuid4())[:8].upper()
    return f"GOV-{timestamp}-{unique}"


@router.get("", response_model=EvaluationListResponse)
async def list_evaluations(
    status: Optional[EvaluationStatus] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List evaluations with pagination and filtering"""
    # Build query
    query = select(Evaluation)

    if status:
        query = query.where(Evaluation.status == status)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Evaluation.created_at.desc())

    result = await db.execute(query)
    evaluations = result.scalars().all()

    return {
        "items": evaluations,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
    }


@router.post("", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED)
async def create_evaluation(
    data: EvaluationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new evaluation"""
    evaluation = Evaluation(
        reference_id=generate_reference_id(),
        title=data.title,
        tender_document_id=data.tender_document_id,
        config=data.config.model_dump() if data.config else {},
        status=EvaluationStatus.DRAFT,
        created_by=current_user.id,
    )

    db.add(evaluation)
    await db.commit()
    await db.refresh(evaluation)

    return evaluation


@router.get("/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(
    evaluation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get evaluation by ID"""
    result = await db.execute(
        select(Evaluation).where(Evaluation.id == evaluation_id)
    )
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found",
        )

    return evaluation


@router.post("/{evaluation_id}/bids")
async def add_bids(
    evaluation_id: str,
    bids: List[BidAdd],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add vendor bids to evaluation"""
    # Verify evaluation exists
    result = await db.execute(
        select(Evaluation).where(Evaluation.id == evaluation_id)
    )
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found",
        )

    if evaluation.status != EvaluationStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add bids to an evaluation that is not in draft status",
        )

    added_count = 0
    for bid_data in bids:
        bid = Bid(
            evaluation_id=evaluation_id,
            vendor_id=bid_data.vendor_id,
            document_id=bid_data.document_id,
            submitted_at=datetime.utcnow(),
        )
        db.add(bid)
        added_count += 1

    await db.commit()

    return {"added": added_count}


@router.patch("/{evaluation_id}/config", response_model=EvaluationResponse)
async def update_config(
    evaluation_id: str,
    config: EvaluationConfig,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update evaluation configuration"""
    result = await db.execute(
        select(Evaluation).where(Evaluation.id == evaluation_id)
    )
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found",
        )

    if evaluation.status != EvaluationStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update config for an evaluation that is not in draft status",
        )

    evaluation.config = config.model_dump()
    await db.commit()
    await db.refresh(evaluation)

    return evaluation


@router.post("/{evaluation_id}/start")
async def start_evaluation(
    evaluation_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Start the evaluation process"""
    result = await db.execute(
        select(Evaluation).where(Evaluation.id == evaluation_id)
    )
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found",
        )

    if evaluation.status != EvaluationStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Evaluation has already been started",
        )

    # Update status
    evaluation.status = EvaluationStatus.PROCESSING
    evaluation.processing_started_at = datetime.utcnow()
    await db.commit()

    # TODO: Add background task to run evaluation
    # background_tasks.add_task(run_evaluation, evaluation_id)

    return {
        "id": evaluation.id,
        "status": evaluation.status.value,
        "estimated_time_seconds": 120,
    }


@router.post("/{evaluation_id}/cancel")
async def cancel_evaluation(
    evaluation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Cancel an evaluation"""
    result = await db.execute(
        select(Evaluation).where(Evaluation.id == evaluation_id)
    )
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found",
        )

    if evaluation.status == EvaluationStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel a completed evaluation",
        )

    evaluation.status = EvaluationStatus.CANCELLED
    await db.commit()

    return {
        "id": evaluation.id,
        "status": evaluation.status.value,
    }


@router.get("/{evaluation_id}/results")
async def get_results(
    evaluation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get evaluation results"""
    result = await db.execute(
        select(Evaluation).where(Evaluation.id == evaluation_id)
    )
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found",
        )

    if evaluation.status != EvaluationStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Evaluation results are not yet available",
        )

    return evaluation.results_summary or {}


@router.get("/{evaluation_id}/results/compliance")
async def get_compliance_results(
    evaluation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get compliance check results"""
    # TODO: Implement compliance results retrieval
    return {"message": "Compliance results"}


@router.get("/{evaluation_id}/results/technical")
async def get_technical_results(
    evaluation_id: str,
    vendor_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get technical evaluation results"""
    # TODO: Implement technical results retrieval
    return {"message": "Technical results"}


@router.get("/{evaluation_id}/results/financial")
async def get_financial_results(
    evaluation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get financial evaluation results"""
    # TODO: Implement financial results retrieval
    return {"message": "Financial results"}


@router.get("/{evaluation_id}/results/comparison")
async def get_comparison_matrix(
    evaluation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get vendor comparison matrix"""
    # TODO: Implement comparison matrix
    return {"message": "Comparison matrix"}


@router.get("/{evaluation_id}/export")
async def export_report(
    evaluation_id: str,
    format: str = Query("pdf", regex="^(pdf|xlsx)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Export evaluation report"""
    # TODO: Implement report export
    return {"message": f"Export report as {format}"}
