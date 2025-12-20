"""
Evaluation Service
Handles evaluation creation, configuration, execution, and results
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import math

from app.models.evaluation import Evaluation, EvaluationStatus
from app.schemas.evaluation import (
    EvaluationCreate,
    EvaluationResponse,
    EvaluationConfig,
    EvaluationResults,
    VendorScore,
)
from app.repositories.evaluation_repository import evaluation_repository
from app.repositories.document_repository import document_repository


class EvaluationService:
    """Service for evaluation management"""

    def __init__(self):
        self.eval_repo = evaluation_repository
        self.doc_repo = document_repository

    def _generate_reference_id(self) -> str:
        """
        Generate a unique reference ID for evaluation

        Format: EVAL-YYYY-NNNNNN

        Returns:
            Generated reference ID
        """
        # Get current year
        year = datetime.utcnow().year

        # Generate a random 6-digit number
        import random
        number = random.randint(1, 999999)

        return f"EVAL-{year}-{number:06d}"

    async def create_evaluation(
        self,
        db: AsyncSession,
        user_id: str,
        data: EvaluationCreate
    ) -> Evaluation:
        """
        Create a new evaluation

        Args:
            db: Database session
            user_id: ID of user creating the evaluation
            data: Evaluation creation data

        Returns:
            Created evaluation instance

        Raises:
            HTTPException: If tender document not found or reference ID collision
        """
        # Validate tender document if provided
        if data.tender_document_id:
            tender_doc = await self.doc_repo.get(db, data.tender_document_id)
            if not tender_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tender document not found"
                )

        # Generate unique reference ID
        max_attempts = 10
        reference_id = None

        for _ in range(max_attempts):
            ref_id = self._generate_reference_id()
            if not await self.eval_repo.reference_id_exists(db, ref_id):
                reference_id = ref_id
                break

        if not reference_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate unique reference ID"
            )

        # Prepare evaluation data
        eval_dict = {
            "reference_id": reference_id,
            "title": data.title,
            "tender_document_id": data.tender_document_id,
            "created_by": user_id,
            "status": EvaluationStatus.DRAFT,
            "config": data.config.model_dump() if data.config else EvaluationConfig().model_dump(),
        }

        # Create evaluation
        evaluation = await self.eval_repo.create(db, eval_dict)

        return evaluation

    async def get_evaluation(
        self,
        db: AsyncSession,
        eval_id: str
    ) -> Evaluation:
        """
        Get evaluation by ID

        Args:
            db: Database session
            eval_id: Evaluation ID

        Returns:
            Evaluation instance

        Raises:
            HTTPException: If evaluation not found
        """
        evaluation = await self.eval_repo.get(db, eval_id)

        if not evaluation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation not found"
            )

        return evaluation

    async def list_evaluations(
        self,
        db: AsyncSession,
        user_id: str,
        page: int = 1,
        limit: int = 20
    ) -> tuple[List[Evaluation], int, int]:
        """
        List evaluations for a user with pagination

        Args:
            db: Database session
            user_id: User ID
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Tuple of (evaluations, total_count, total_pages)
        """
        # Calculate skip
        skip = (page - 1) * limit

        # Get evaluations
        evaluations = await self.eval_repo.get_by_user(db, user_id, skip, limit)

        # Get total count
        total = await self.eval_repo.count_by_user(db, user_id)

        # Calculate total pages
        total_pages = math.ceil(total / limit) if total > 0 else 1

        return evaluations, total, total_pages

    async def update_evaluation_config(
        self,
        db: AsyncSession,
        eval_id: str,
        config: EvaluationConfig
    ) -> Evaluation:
        """
        Update evaluation configuration

        Args:
            db: Database session
            eval_id: Evaluation ID
            config: New configuration

        Returns:
            Updated evaluation

        Raises:
            HTTPException: If evaluation not found or not in draft status
        """
        evaluation = await self.get_evaluation(db, eval_id)

        # Only allow config update in draft status
        if evaluation.status != EvaluationStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only update configuration for draft evaluations"
            )

        # Update config
        update_data = {"config": config.model_dump()}
        evaluation = await self.eval_repo.update(db, evaluation, update_data)

        return evaluation

    async def start_evaluation(
        self,
        db: AsyncSession,
        eval_id: str
    ) -> Evaluation:
        """
        Start evaluation process

        Args:
            db: Database session
            eval_id: Evaluation ID

        Returns:
            Updated evaluation

        Raises:
            HTTPException: If evaluation not found or not in draft status
        """
        evaluation = await self.eval_repo.get_with_bids(db, eval_id)

        if not evaluation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation not found"
            )

        # Check if in draft status
        if evaluation.status != EvaluationStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Evaluation already started or completed"
            )

        # Check if there are bids
        if not evaluation.bids or len(evaluation.bids) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot start evaluation without bids"
            )

        # Update status and start time
        update_data = {
            "status": EvaluationStatus.PROCESSING,
            "processing_started_at": datetime.utcnow(),
        }

        evaluation = await self.eval_repo.update(db, evaluation, update_data)

        # TODO: Trigger async evaluation process with agents
        # This would typically:
        # 1. Queue the evaluation job
        # 2. Run multi-agent analysis
        # 3. Update results when complete

        return evaluation

    async def get_evaluation_results(
        self,
        db: AsyncSession,
        eval_id: str
    ) -> EvaluationResults:
        """
        Get evaluation results

        Args:
            db: Database session
            eval_id: Evaluation ID

        Returns:
            Evaluation results

        Raises:
            HTTPException: If evaluation not found or not completed
        """
        evaluation = await self.eval_repo.get_with_bids(db, eval_id)

        if not evaluation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation not found"
            )

        # Check if evaluation is completed
        if evaluation.status != EvaluationStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Evaluation is not completed (status: {evaluation.status})"
            )

        # Parse results from results_summary
        results_summary = evaluation.results_summary or {}

        # Calculate processing time
        processing_time = 0
        if evaluation.processing_started_at and evaluation.processing_completed_at:
            delta = evaluation.processing_completed_at - evaluation.processing_started_at
            processing_time = int(delta.total_seconds())

        # Build results response
        results = EvaluationResults(
            evaluation_id=evaluation.id,
            status=evaluation.status,
            method=evaluation.config.get("method", "qcbs"),
            total_bids=len(evaluation.bids),
            qualified_bids=results_summary.get("qualified_bids", 0),
            disqualified_bids=results_summary.get("disqualified_bids", 0),
            winner=results_summary.get("winner"),
            rankings=results_summary.get("rankings", []),
            score_distribution=results_summary.get("score_distribution", {}),
            processing_time_seconds=processing_time,
            completed_at=evaluation.processing_completed_at,
        )

        return results


# Singleton instance
evaluation_service = EvaluationService()
