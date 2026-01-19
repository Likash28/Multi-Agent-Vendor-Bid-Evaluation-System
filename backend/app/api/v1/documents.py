"""
Document Endpoints
"""

import os
import aiofiles
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.dependencies import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.document import Document
from app.config import settings
from app.utils.file_utils import (
    validate_file_type,
    validate_file_size,
    get_file_hash_from_bytes,
    detect_mime_type,
    sanitize_filename,
    ensure_directory_exists,
)
from app.schemas.document import DocumentResponse
from app.utils.logger import get_logger, log_request, log_response, log_document_event, log_error

router = APIRouter()
logger = get_logger(__name__)


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    file_type: str = Form(...),  # tender, bid
    metadata: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Upload a document"""
    log_request(logger, "POST", "/api/v1/documents/upload", user_id=current_user.id, 
                filename=file.filename, file_type=file_type)
    
    try:
        # Check if filename is provided
        if not file.filename:
            logger.warning(f"Upload attempt without filename by user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required",
            )
        
        logger.info(f"Processing document upload: {file.filename} (type: {file_type}) by user {current_user.id}")
        
        # Validate file type
        allowed_extensions = [f".{ext.strip()}" for ext in settings.ALLOWED_FILE_TYPES.split(",")]
        if not validate_file_type(file.filename, allowed_extensions):
            logger.warning(f"Invalid file type attempted: {file.filename} by user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {settings.ALLOWED_FILE_TYPES}",
            )

        # Read file content
        content = await file.read()
        file_size = len(content)
        logger.debug(f"File read: {file.filename}, size: {file_size} bytes")

        # Validate file size
        if not validate_file_size(file_size, settings.MAX_UPLOAD_SIZE):
            logger.warning(f"File size exceeded: {file.filename} ({file_size} bytes) by user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes",
            )

        # Generate file hash
        file_hash = get_file_hash_from_bytes(content)
        logger.debug(f"File hash generated: {file_hash}")

        # Sanitize filename
        safe_filename = sanitize_filename(file.filename)

        # Create storage path
        upload_dir = Path(settings.UPLOAD_DIR)
        ensure_directory_exists(upload_dir)
        file_path = upload_dir / f"{file_hash}_{safe_filename}"

        # Save file
        file_path_str = str(file_path)
        logger.info(f"Saving file to: {file_path_str}")
        async with aiofiles.open(file_path_str, "wb") as f:
            await f.write(content)

        # Create document record
        document = Document(
            filename=safe_filename,
            original_filename=file.filename,  # Store original filename
            file_path=file_path_str,
            file_type=file_type,
            file_size=len(content),
            mime_type=detect_mime_type(safe_filename),
            file_hash=file_hash,
            uploaded_by_id=current_user.id,
        )

        db.add(document)
        await db.commit()
        await db.refresh(document)

        logger.info(f"Document uploaded successfully: {document.id} - {file.filename} by user {current_user.id}")
        log_document_event(logger, "upload", document.id, current_user.id, 
                          filename=file.filename, file_type=file_type, file_size=file_size)
        log_response(logger, "POST", "/api/v1/documents/upload", status.HTTP_201_CREATED, 
                    user_id=current_user.id, document_id=document.id)
        return document
    except HTTPException:
        raise
    except Exception as e:
        log_error(logger, e, f"Document upload - {file.filename if file.filename else 'unknown'}")
        log_response(logger, "POST", "/api/v1/documents/upload", status.HTTP_500_INTERNAL_SERVER_ERROR,
                    user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get document by ID"""
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Download document file"""
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if not os.path.exists(document.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found on server",
        )

    return FileResponse(
        path=document.file_path,
        filename=document.filename,
        media_type=document.mime_type,
    )
