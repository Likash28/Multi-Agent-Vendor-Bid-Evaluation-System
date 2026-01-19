"""
Reports Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime
from pydantic import BaseModel

from app.dependencies import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.evaluation import Evaluation, EvaluationStatus

router = APIRouter()


class ReportResponse(BaseModel):
    """Schema for report response"""
    id: str
    evaluation_id: str
    evaluation_title: str
    format: str
    status: str
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    generated_at: str
    generated_by: str

    class Config:
        from_attributes = False


@router.get("", response_model=List[ReportResponse])
async def list_reports(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    format: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all evaluation reports"""
    # Query completed evaluations that have reports
    query = select(Evaluation).where(
        Evaluation.status == EvaluationStatus.COMPLETED
    ).where(
        Evaluation.results_summary.isnot(None)
    ).options(selectinload(Evaluation.created_by_user))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Evaluation.processing_completed_at.desc())

    result = await db.execute(query)
    evaluations = result.scalars().all()

    # Convert evaluations to report format
    reports = []
    for evaluation in evaluations:
        if not evaluation.results_summary or "report_markdown" not in evaluation.results_summary:
            continue

        # Get report metadata
        report_metadata = evaluation.results_summary.get("report_metadata", {})
        generated_at = report_metadata.get("generated_at")
        if not generated_at and evaluation.processing_completed_at:
            generated_at = evaluation.processing_completed_at.isoformat()
        elif not generated_at:
            generated_at = evaluation.updated_at.isoformat()

        # Get creator info
        creator_name = "System"
        if evaluation.created_by_user:
            creator_name = evaluation.created_by_user.name or evaluation.created_by_user.email

        # Build file URL (PDF endpoint)
        file_url = f"/api/v1/evaluations/{evaluation.id}/report/pdf"

        # Calculate file size (approximate - markdown length)
        markdown_content = evaluation.results_summary.get("report_markdown", "")
        file_size = len(markdown_content.encode('utf-8'))

        report = ReportResponse(
            id=evaluation.id,
            evaluation_id=evaluation.id,
            evaluation_title=evaluation.title,
            format="PDF",
            status="COMPLETED",
            file_url=file_url,
            file_size=file_size,
            generated_at=generated_at,
            generated_by=creator_name,
        )

        # Filter by format if specified
        if format and format.upper() != "PDF":
            continue

        reports.append(report)

    return reports

