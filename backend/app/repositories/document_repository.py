"""
Document Repository
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document, dict, dict]):
    """Repository for Document model operations"""

    def __init__(self):
        super().__init__(Document)

    async def get_by_hash(self, db: AsyncSession, file_hash: str) -> Optional[Document]:
        """
        Get document by file hash (for duplicate detection)

        Args:
            db: Database session
            file_hash: SHA-256 file hash

        Returns:
            Document instance or None if not found
        """
        result = await db.execute(
            select(Document).where(Document.file_hash == file_hash)
        )
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """
        Get documents uploaded by a specific user

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of documents
        """
        result = await db.execute(
            select(Document)
            .where(Document.uploaded_by == user_id)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_type(
        self,
        db: AsyncSession,
        file_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """
        Get documents by file type (tender, bid, etc.)

        Args:
            db: Database session
            file_type: File type
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of documents
        """
        result = await db.execute(
            select(Document)
            .where(Document.file_type == file_type)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


# Singleton instance
document_repository = DocumentRepository()
