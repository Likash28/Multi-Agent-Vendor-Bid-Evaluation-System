"""
Document Service
Handles document upload, storage, and content extraction
"""

from typing import Dict, Any, Optional
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, UploadFile
import logging

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
from app.utils.logger import get_logger, log_document_event, log_error

logger = get_logger(__name__)


class DocumentService:
    """Service for document management and processing"""

    def __init__(self):
        self.doc_repo = document_repository
        self.pdf_parser = PDFParser()
        self.docx_parser = DocxParser()
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.allowed_types = ['.pdf', '.docx', '.doc']
        self.max_size = settings.MAX_UPLOAD_SIZE  # Already in bytes

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
            max_size_mb = self.max_size / (1024 * 1024)  # Convert bytes to MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {max_size_mb:.0f}MB"
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
        logger.info(f"Processing document: {doc_id}")
        log_document_event(logger, "processing_started", doc_id)
        
        try:
            document = await self.get_document(db, doc_id)
            file_path = Path(document.file_path)

            if not file_path.exists():
                logger.error(f"Document file not found: {file_path} for document {doc_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document file not found on disk"
                )

            logger.debug(f"Extracting content from {document.filename} (type: {document.file_type})")
            
            # Extract content based on file type
            try:
                file_ext = file_path.suffix.lower()

                if file_ext == '.pdf':
                    logger.debug(f"Parsing PDF: {file_path}")
                    content = self.pdf_parser.parse_document(file_path)
                elif file_ext in ['.docx', '.doc']:
                    logger.debug(f"Parsing DOCX: {file_path}")
                    content = self.docx_parser.parse_document(file_path)
                else:
                    logger.warning(f"Unsupported file type: {file_ext} for document {doc_id}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Unsupported file type: {file_ext}"
                    )

                logger.info(f"Document parsed successfully: {doc_id}, text length: {len(content.text)}, pages: {content.page_count}")

                # Prepare extracted data - store text in the JSON field
                extracted_data = {
                    "text": content.text,  # Store the actual text content
                    "text_length": len(content.text),
                    "table_count": len(content.tables),
                    "page_count": content.page_count,
                    "metadata": content.metadata,
                }

                # Update document with extracted content
                update_data = {
                    "extracted_data": extracted_data,
                }

                await self.doc_repo.update(db, document, update_data)
                
                logger.info(f"Document processing completed: {doc_id}")
                log_document_event(logger, "processing_completed", doc_id, 
                                  text_length=len(content.text), page_count=content.page_count)

                return {
                    "document_id": doc_id,
                    "text": content.text,
                    "tables": content.tables,
                    "metadata": content.metadata,
                    "extracted_data": extracted_data,
                }

            except HTTPException:
                raise
            except Exception as e:
                log_error(logger, e, f"Document processing - {doc_id}")
                log_document_event(logger, "processing_failed", doc_id, error=str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to process document: {str(e)}"
                )
        except HTTPException:
            raise
        except Exception as e:
            log_error(logger, e, f"Document processing - {doc_id}")
            raise


# Singleton instance
document_service = DocumentService()
