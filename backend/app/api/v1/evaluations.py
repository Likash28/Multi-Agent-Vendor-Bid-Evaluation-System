"""
Evaluation Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime
import uuid
import logging

from app.dependencies import get_db, AsyncSessionLocal
from app.core.auth import get_current_active_user, require_permission, Permission
from app.models.user import User
from app.models.evaluation import Evaluation, EvaluationStatus, EvaluationMethod
from app.models.bid import Bid
from app.models.document import Document
from app.schemas.evaluation import (
    EvaluationCreate,
    EvaluationResponse,
    EvaluationListResponse,
    EvaluationSummary,
    EvaluationConfig,
    BidAdd,
)
from pydantic import BaseModel
from app.services.document_service import document_service
from app.config import settings
from app.utils.logger import get_logger, log_request, log_response, log_evaluation_event, log_error

router = APIRouter()
logger = get_logger(__name__)


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
    log_request(logger, "POST", "/api/v1/evaluations", user_id=current_user.id, title=data.title)
    
    try:
        logger.info(f"Creating evaluation: {data.title} by user {current_user.id}")
        
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

        logger.info(f"Evaluation created: {evaluation.id} - {evaluation.reference_id}")
        log_evaluation_event(logger, "created", evaluation.id, user_id=current_user.id,
                           title=data.title, method=data.config.method if data.config else None)
        log_response(logger, "POST", "/api/v1/evaluations", status.HTTP_201_CREATED,
                    user_id=current_user.id, evaluation_id=evaluation.id)
        return evaluation
    except Exception as e:
        log_error(logger, e, "Create evaluation")
        log_response(logger, "POST", "/api/v1/evaluations", status.HTTP_500_INTERNAL_SERVER_ERROR,
                    user_id=current_user.id)
        raise


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


class EvaluationUpdate(BaseModel):
    """Schema for updating evaluation"""
    title: Optional[str] = None
    tender_document_id: Optional[str] = None


@router.patch("/{evaluation_id}", response_model=EvaluationResponse)
async def update_evaluation(
    evaluation_id: str,
    updates: EvaluationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update evaluation fields"""
    result = await db.execute(
        select(Evaluation).where(Evaluation.id == evaluation_id)
    )
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found",
        )

    # Only allow updates to DRAFT evaluations
    if evaluation.status != EvaluationStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update evaluations in DRAFT status",
        )

    # Update fields
    if updates.title is not None:
        evaluation.title = updates.title
    if updates.tender_document_id is not None:
        evaluation.tender_document_id = updates.tender_document_id

    await db.commit()
    await db.refresh(evaluation)

    return evaluation


@router.delete("/{evaluation_id}")
async def delete_evaluation(
    evaluation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete an evaluation"""
    result = await db.execute(
        select(Evaluation).where(Evaluation.id == evaluation_id)
    )
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found",
        )

    # Only allow deletion of DRAFT or CANCELLED evaluations
    if evaluation.status not in [EvaluationStatus.DRAFT, EvaluationStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only delete evaluations in DRAFT or CANCELLED status",
        )

    # Delete related bids first (cascade)
    bids_result = await db.execute(
        select(Bid).where(Bid.evaluation_id == evaluation_id)
    )
    bids = bids_result.scalars().all()
    for bid in bids:
        await db.delete(bid)

    # Delete the evaluation
    await db.delete(evaluation)
    await db.commit()

    return {"message": "Evaluation deleted successfully"}


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
    log_request(logger, "POST", f"/api/v1/evaluations/{evaluation_id}/start", user_id=current_user.id)
    log_evaluation_event(logger, "start_requested", evaluation_id, user_id=current_user.id)
    
    try:
        result = await db.execute(
            select(Evaluation).where(Evaluation.id == evaluation_id)
        )
        evaluation = result.scalar_one_or_none()

        if not evaluation:
            logger.warning(f"Evaluation not found: {evaluation_id} by user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation not found",
            )

        if evaluation.status != EvaluationStatus.DRAFT:
            logger.warning(f"Evaluation already started: {evaluation_id}, status: {evaluation.status}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Evaluation has already been started",
            )

        logger.info(f"Starting evaluation: {evaluation_id} by user {current_user.id}")
        
        # Update status
        evaluation.status = EvaluationStatus.PROCESSING
        evaluation.processing_started_at = datetime.utcnow()
        await db.commit()

        log_evaluation_event(logger, "started", evaluation_id, user_id=current_user.id, 
                           status="PROCESSING", method=evaluation.config.get("method"))

        # Start background task to run evaluation
        background_tasks.add_task(run_evaluation_task, evaluation_id)
        logger.info(f"Background task scheduled for evaluation: {evaluation_id}")

        log_response(logger, "POST", f"/api/v1/evaluations/{evaluation_id}/start", status.HTTP_200_OK,
                    user_id=current_user.id, evaluation_id=evaluation_id)
        return {
            "id": evaluation.id,
            "status": evaluation.status.value,
            "estimated_time_seconds": 120,
        }
    except HTTPException:
        raise
    except Exception as e:
        log_error(logger, e, f"Start evaluation - {evaluation_id}")
        log_evaluation_event(logger, "start_failed", evaluation_id, user_id=current_user.id, error=str(e))
        raise


async def run_evaluation_task(evaluation_id: str):
    """
    Background task to run the complete evaluation workflow.
    
    This function:
    1. Loads evaluation with bids and documents
    2. Extracts content from tender and bid documents
    3. Runs the orchestrator with Bedrock agents
    4. Saves results to database
    """
    # Lazy import to avoid import errors at startup
    from app.agents.orchestrator import EvaluationOrchestrator
    from app.agents.schemas import EvaluationMethod as AgentEvaluationMethod
    
    async with AsyncSessionLocal() as db:
        try:
            log_evaluation_event(logger, "task_started", evaluation_id)
            logger.info(f"Starting evaluation task for {evaluation_id}")
            
            # Load evaluation with bids
            result = await db.execute(
                select(Evaluation)
                .where(Evaluation.id == evaluation_id)
                .options(selectinload(Evaluation.bids), selectinload(Evaluation.tender_document))
            )
            evaluation = result.scalar_one_or_none()
            
            if not evaluation:
                log_evaluation_event(logger, "task_failed", evaluation_id, error="Evaluation not found")
                logger.error(f"Evaluation {evaluation_id} not found")
                return
            
            logger.info(f"Evaluation loaded: {evaluation_id}, status: {evaluation.status}, bids: {len(evaluation.bids) if evaluation.bids else 0}")
            
            # Check if evaluation has bids
            if not evaluation.bids or len(evaluation.bids) == 0:
                log_evaluation_event(logger, "task_failed", evaluation_id, error="No bids found")
                logger.error(f"Evaluation {evaluation_id} has no bids")
                evaluation.status = EvaluationStatus.FAILED
                evaluation.processing_completed_at = datetime.utcnow()
                await db.commit()
                return
            
            # Load tender document and extract content
            tender_requirements = {}
            if evaluation.tender_document_id:
                tender_doc_result = await db.execute(
                    select(Document).where(Document.id == evaluation.tender_document_id)
                )
                tender_doc = tender_doc_result.scalar_one_or_none()
                
                if tender_doc:
                    # Extract content if not already extracted
                    extracted_text = tender_doc.extracted_data.get("text", "") if tender_doc.extracted_data else ""
                    if not extracted_text:
                        doc_content = await document_service.process_document(db, tender_doc.id)
                        tender_requirements = {
                            "text": doc_content.get("text", ""),
                            "metadata": doc_content.get("metadata", {}),
                        }
                    else:
                        tender_requirements = {
                            "text": extracted_text,
                            "metadata": tender_doc.extracted_data.get("metadata", {}) if tender_doc.extracted_data else {},
                        }
            
            # Load bid documents and extract content
            bids_data = []
            for bid in evaluation.bids:
                if not bid.document_id:
                    logger.warning(f"Bid {bid.id} has no document_id")
                    continue
                
                bid_doc_result = await db.execute(
                    select(Document).where(Document.id == bid.document_id)
                )
                bid_doc = bid_doc_result.scalar_one_or_none()
                
                if not bid_doc:
                    logger.warning(f"Bid document {bid.document_id} not found")
                    continue
                
                # Extract content if not already extracted
                extracted_text = bid_doc.extracted_data.get("text", "") if bid_doc.extracted_data else ""
                if not extracted_text:
                    doc_content = await document_service.process_document(db, bid_doc.id)
                    document_content = doc_content.get("text", "")
                else:
                    document_content = extracted_text
                
                bids_data.append({
                    "bid_id": bid.id,
                    "vendor_id": bid.vendor_id,
                    "document_content": document_content,
                })
            
            if not bids_data:
                logger.error(f"No valid bid documents found for evaluation {evaluation_id}")
                evaluation.status = EvaluationStatus.FAILED
                await db.commit()
                return
            
            # Map evaluation method from model format to agent format
            method_map = {
                "l1": AgentEvaluationMethod.L1,
                "qcbs": AgentEvaluationMethod.QCBS,
                "two_stage": AgentEvaluationMethod.TWO_STAGE,
            }
            config_method = evaluation.config.get("method", "qcbs")
            agent_method = method_map.get(config_method, AgentEvaluationMethod.QCBS)
            
            # Initialize orchestrator with Bedrock settings
            orchestrator = EvaluationOrchestrator(
                model_id=settings.BEDROCK_MODEL_ID,
                region_name=settings.AWS_REGION,
            )
            
            # Run evaluation workflow
            logger.info(f"Running orchestrator for evaluation {evaluation_id} with {len(bids_data)} bids, method: {agent_method}")
            log_evaluation_event(logger, "orchestrator_started", evaluation_id, 
                               bid_count=len(bids_data), method=config_method)
            
            result = await orchestrator.run(
                evaluation_id=evaluation_id,
                bids=bids_data,
                tender_requirements=tender_requirements,
                evaluation_method=agent_method,
            )
            
            logger.info(f"Orchestrator completed for evaluation {evaluation_id}, status: {result.status}")
            
            # Update evaluation with results
            if result.status == "completed" and result.report:
                logger.info(f"Evaluation completed successfully: {evaluation_id}")
                log_evaluation_event(logger, "orchestrator_completed", evaluation_id, status="completed")
                evaluation.status = EvaluationStatus.COMPLETED
                evaluation.processing_completed_at = datetime.utcnow()
                
                # Import report agent to convert report to markdown
                from app.agents.report_agent import ReportAgent
                report_agent = ReportAgent()
                
                # Convert report to markdown
                report_markdown = report_agent.export_to_markdown(result.report)
                
                # Extract rankings from comparison_result
                rankings = []
                if result.report.comparison_result and result.report.comparison_result.rankings:
                    rankings = [
                        {
                            "rank": r.rank,
                            "bid_id": r.bid_id,
                            "vendor_name": r.vendor_name,
                            "technical_score": r.technical_score,
                            "financial_score": r.financial_score,
                            "combined_score": r.combined_score,
                            "is_compliant": r.is_compliant,
                            "is_winner": r.is_winner,
                            "qualified": r.is_compliant,
                        }
                        for r in result.report.comparison_result.rankings
                    ]
                
                # Save results summary with report markdown
                evaluation.results_summary = {
                    "qualified_bids": len([r for r in rankings if r.get("qualified", False)]),
                    "disqualified_bids": len([r for r in rankings if not r.get("qualified", False)]),
                    "winner": rankings[0] if rankings else None,
                    "rankings": rankings,
                    "score_distribution": {},
                    "execution_time_seconds": result.execution_time_seconds,
                    "report_markdown": report_markdown,
                    "report_metadata": {
                        "tender_reference": result.report.tender_reference,
                        "tender_title": result.report.tender_title,
                        "evaluation_method": result.report.evaluation_method.value,
                        "generated_at": result.report.generated_at.isoformat() if result.report.generated_at else None,
                    }
                }
                
                # Set winner bid if available
                if rankings:
                    winner_rank = rankings[0]
                    winner_bid_id = winner_rank.get("bid_id")
                    if winner_bid_id:
                        evaluation.winner_bid_id = winner_bid_id
            elif result.status == "failed":
                evaluation.status = EvaluationStatus.FAILED
                evaluation.processing_completed_at = datetime.utcnow()
                evaluation.results_summary = {
                    "errors": result.errors,
                    "status": "failed",
                }
            else:
                evaluation.status = EvaluationStatus.FAILED
                evaluation.processing_completed_at = datetime.utcnow()
                evaluation.results_summary = {
                    "errors": result.errors or ["Unknown error"],
                    "status": "failed",
                }
            
            await db.commit()
            logger.info(f"Evaluation {evaluation_id} completed with status: {result.status}")
            
        except Exception as e:
            logger.error(f"Error running evaluation {evaluation_id}: {str(e)}", exc_info=True)
            try:
                # Update evaluation status to failed
                result = await db.execute(
                    select(Evaluation).where(Evaluation.id == evaluation_id)
                )
                evaluation = result.scalar_one_or_none()
                if evaluation:
                    evaluation.status = EvaluationStatus.FAILED
                    evaluation.processing_completed_at = datetime.utcnow()
                    evaluation.results_summary = {
                        "errors": [str(e)],
                        "status": "failed",
                    }
                    await db.commit()
            except Exception as commit_error:
                logger.error(f"Failed to update evaluation status: {str(commit_error)}")


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


@router.get("/{evaluation_id}/report")
async def get_report(
    evaluation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get evaluation report content"""
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
            detail="Report is not yet available. Evaluation must be completed.",
        )

    if not evaluation.results_summary or "report_markdown" not in evaluation.results_summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found for this evaluation",
        )

    report_metadata = evaluation.results_summary.get("report_metadata", {})
    
    return {
        "markdown": evaluation.results_summary["report_markdown"],
        "metadata": {
            "evaluation_id": evaluation_id,
            "title": evaluation.title,
            "method": report_metadata.get("evaluation_method", evaluation.config.get("method", "qcbs")),
            "generated_at": report_metadata.get("generated_at") or evaluation.processing_completed_at.isoformat() if evaluation.processing_completed_at else None,
            "winner": evaluation.results_summary.get("winner", {}).get("vendor_name") if evaluation.results_summary.get("winner") else None,
        }
    }


@router.get("/{evaluation_id}/report/pdf")
async def get_report_pdf(
    evaluation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Download evaluation report as PDF"""
    from fastapi.responses import Response
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from io import BytesIO
    import re
    
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
            detail="Report is not yet available. Evaluation must be completed.",
        )

    if not evaluation.results_summary or "report_markdown" not in evaluation.results_summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found for this evaluation",
        )

    # Get markdown content
    markdown_content = evaluation.results_summary["report_markdown"]
    
    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='#1a1a1a',
        spaceAfter=12,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#2c3e50',
        spaceAfter=8,
    )
    
    # Parse markdown and convert to PDF elements
    story = []
    
    # Simple markdown to PDF conversion
    lines = markdown_content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.2 * inch))
            continue
            
        # Handle headers
        if line.startswith('# '):
            story.append(Paragraph(line[2:], title_style))
            story.append(Spacer(1, 0.3 * inch))
        elif line.startswith('## '):
            story.append(Paragraph(line[3:], heading_style))
            story.append(Spacer(1, 0.2 * inch))
        elif line.startswith('### '):
            story.append(Paragraph(line[4:], styles['Heading3']))
            story.append(Spacer(1, 0.15 * inch))
        elif line.startswith('**') and line.endswith('**'):
            # Bold text
            text = line.replace('**', '')
            story.append(Paragraph(f"<b>{text}</b>", styles['Normal']))
        elif line.startswith('- '):
            # Bullet point
            text = line[2:].replace('**', '')
            story.append(Paragraph(f"• {text}", styles['Normal']))
        else:
            # Regular paragraph - handle inline bold
            text = line
            # Convert **text** to <b>text</b>
            text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
            if text:
                story.append(Paragraph(text, styles['Normal']))
                story.append(Spacer(1, 0.1 * inch))
    
    # Build PDF
    doc.build(story)
    
    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    # Return PDF response
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="evaluation-report-{evaluation_id}.pdf"'
        }
    )


@router.get("/{evaluation_id}/export")
async def export_report(
    evaluation_id: str,
    format: str = Query("pdf", regex="^(pdf|xlsx)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Export evaluation report"""
    if format == "pdf":
        # Redirect to PDF endpoint
        return await get_report_pdf(evaluation_id, db, current_user)
    else:
        # TODO: Implement XLSX export
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="XLSX export not yet implemented",
        )
