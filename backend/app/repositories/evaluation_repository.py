"""
Evaluation Repository
"""

from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.evaluation import Evaluation, EvaluationStatus
from app.repositories.base import BaseRepository
from app.schemas.evaluation import EvaluationCreate


class EvaluationRepository(BaseRepository[Evaluation, EvaluationCreate, dict]):
    """Repository for Evaluation model operations"""

    def __init__(self):
        super().__init__(Evaluation)

    async def get_by_reference_id(
        self,
        db: AsyncSession,
        reference_id: str
    ) -> Optional[Evaluation]:
        """
        Get evaluation by reference ID

        Args:
            db: Database session
            reference_id: Evaluation reference ID

        Returns:
            Evaluation instance or None if not found
        """
        result = await db.execute(
            select(Evaluation).where(Evaluation.reference_id == reference_id)
        )
        return result.scalar_one_or_none()

    async def get_with_bids(
        self,
        db: AsyncSession,
        evaluation_id: str
    ) -> Optional[Evaluation]:
        """
        Get evaluation with all related bids

        Args:
            db: Database session
            evaluation_id: Evaluation ID

        Returns:
            Evaluation instance with bids loaded or None
        """
        result = await db.execute(
            select(Evaluation)
            .where(Evaluation.id == evaluation_id)
            .options(selectinload(Evaluation.bids))
        )
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Evaluation]:
        """
        Get evaluations created by a specific user

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of evaluations
        """
        result = await db.execute(
            select(Evaluation)
            .where(Evaluation.created_by == user_id)
            .order_by(Evaluation.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_user(self, db: AsyncSession, user_id: str) -> int:
        """
        Count evaluations by user

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Number of evaluations
        """
        result = await db.execute(
            select(func.count(Evaluation.id)).where(Evaluation.created_by == user_id)
        )
        return result.scalar_one()

    async def get_by_status(
        self,
        db: AsyncSession,
        status: EvaluationStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Evaluation]:
        """
        Get evaluations by status

        Args:
            db: Database session
            status: Evaluation status
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of evaluations
        """
        result = await db.execute(
            select(Evaluation)
            .where(Evaluation.status == status)
            .order_by(Evaluation.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def reference_id_exists(self, db: AsyncSession, reference_id: str) -> bool:
        """
        Check if reference ID already exists

        Args:
            db: Database session
            reference_id: Reference ID to check

        Returns:
            True if exists, False otherwise
        """
        result = await db.execute(
            select(Evaluation.id).where(Evaluation.reference_id == reference_id)
        )
        return result.scalar_one_or_none() is not None


# Singleton instance
evaluation_repository = EvaluationRepository()
