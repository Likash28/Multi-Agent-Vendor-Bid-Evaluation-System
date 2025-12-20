"""
Document Service
Handles document upload, storage, and content extraction
"""

from typing import Dict, Any, Optional
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, UploadFile

from app.models.document import Document
from app.repositories.document_repository import document_repository
from app.utils.file_utils import (
    save_upload_file,
    get_file_hash,
    validate_file_type,
    get_mime_type,
    ensure_directory,
)
from app.utils.pdf_parser import PDFParser
from app.utils.docx_parser import DocxParser
from app.config import settings


class DocumentService:
    """Service for document management and processing"""

    def __init__(self):
        self.doc_repo = document_repository
        self.pdf_parser = PDFParser()
        self.docx_parser = DocxParser()
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.allowed_types = ['.pdf', '.docx', '.doc']
        self.max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024  # Convert to bytes

    async def upload_document(
        self,
        db: AsyncSession,
        user_id: str,
        file: UploadFile,
        file_type: str = "bid"
    ) -> Document:
        """
        Upload and save a document

        Args:
            db: Database session
            user_id: ID of user uploading the document
            file: Uploaded file
            file_type: Type of document (tender, bid, etc.)

        Returns:
            Created document instance

        Raises:
            HTTPException: If file validation fails
        """
        # Validate file type
        if not validate_file_type(file.filename, self.allowed_types):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(self.allowed_types)}"
            )

        # Validate file size (approximate check)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        if file_size > self.max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB"
            )

        # Ensure upload directory exists
        ensure_directory(self.upload_dir)

        # Generate unique file path
        from datetime import datetime
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_ext = Path(file.filename).suffix
        safe_filename = f"{user_id}_{timestamp}_{file.filename}"
        file_path = self.upload_dir / safe_filename

        # Save file
        try:
            await save_upload_file(file, file_path)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )

        # Calculate file hash
        try:
            file_hash = await get_file_hash(file_path)
        except Exception as e:
            # Clean up file if hash calculation fails
            file_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to calculate file hash: {str(e)}"
            )

        # Check for duplicate (same hash)
        existing_doc = await self.doc_repo.get_by_hash(db, file_hash)
        if existing_doc:
            # Remove uploaded file since it's a duplicate
            file_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document already exists (duplicate file)"
            )

        # Get MIME type
        mime_type = get_mime_type(file_path)

        # Create document record
        doc_dict = {
            "filename": file.filename,
            "file_path": str(file_path),
            "file_type": file_type,
            "file_size": file_size,
            "mime_type": mime_type,
            "file_hash": file_hash,
            "uploaded_by": user_id,
        }

        document = await self.doc_repo.create(db, doc_dict)

        return document

    async def get_document(
        self,
        db: AsyncSession,
        doc_id: str
    ) -> Document:
        """
        Get document by ID

        Args:
            db: Database session
            doc_id: Document ID

        Returns:
            Document instance

        Raises:
            HTTPException: If document not found
        """
        document = await self.doc_repo.get(db, doc_id)

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        return document

    async def delete_document(
        self,
        db: AsyncSession,
        doc_id: str
    ) -> None:
        """
        Delete a document

        Args:
            db: Database session
            doc_id: Document ID

        Raises:
            HTTPException: If document not found
        """
        document = await self.get_document(db, doc_id)

        # Delete physical file
        file_path = Path(document.file_path)
        if file_path.exists():
            file_path.unlink()

        # Delete database record
        await self.doc_repo.delete(db, doc_id)

    async def process_document(
        self,
        db: AsyncSession,
        doc_id: str
    ) -> Dict[str, Any]:
        """
        Extract content from a document

        Args:
            db: Database session
            doc_id: Document ID

        Returns:
            Dictionary with extracted content

        Raises:
            HTTPException: If document not found or processing fails
        """
        document = await self.get_document(db, doc_id)
        file_path = Path(document.file_path)

        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document file not found on disk"
            )

        # Extract content based on file type
        try:
            file_ext = file_path.suffix.lower()

            if file_ext == '.pdf':
                content = self.pdf_parser.parse_document(file_path)
            elif file_ext in ['.docx', '.doc']:
                content = self.docx_parser.parse_document(file_path)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported file type: {file_ext}"
                )

            # Prepare extracted data
            extracted_data = {
                "text_length": len(content.text),
                "table_count": len(content.tables),
                "page_count": content.page_count,
                "metadata": content.metadata,
            }

            # Update document with extracted content
            update_data = {
                "extracted_text": content.text,
                "extracted_data": extracted_data,
            }

            await self.doc_repo.update(db, document, update_data)

            return {
                "document_id": doc_id,
                "text": content.text,
                "tables": content.tables,
                "metadata": content.metadata,
                "extracted_data": extracted_data,
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process document: {str(e)}"
            )


# Singleton instance
document_service = DocumentService()
