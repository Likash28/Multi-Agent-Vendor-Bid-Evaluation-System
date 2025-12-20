"""
File handling utilities for upload, validation, and management
"""

import hashlib
import mimetypes
import re
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import UploadFile
import aiofiles


def validate_file_size(file_size: int, max_size: int) -> bool:
    """
    Validate if file size is within allowed limit

    Args:
        file_size: Size of the file in bytes
        max_size: Maximum allowed size in bytes

    Returns:
        bool: True if file size is within limit
    """
    return file_size <= max_size


def get_file_hash_from_bytes(content: bytes) -> str:
    """
    Calculate SHA-256 hash from file content bytes

    Args:
        content: File content as bytes

    Returns:
        str: SHA-256 hash in hexadecimal format
    """
    return hashlib.sha256(content).hexdigest()


def detect_mime_type(filename: str, content: Optional[bytes] = None) -> str:
    """
    Detect MIME type from filename and optionally file content

    Args:
        filename: Name of the file
        content: Optional file content for magic byte detection

    Returns:
        str: MIME type (e.g., 'application/pdf')
    """
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to remove unsafe characters

    Args:
        filename: Original filename

    Returns:
        str: Sanitized filename with UUID prefix for uniqueness
    """
    # Remove path components
    filename = Path(filename).name
    # Replace unsafe characters
    safe_name = re.sub(r'[^\w\-_.]', '_', filename)
    # Add UUID prefix for uniqueness
    unique_prefix = str(uuid.uuid4())[:8]
    return f"{unique_prefix}_{safe_name}"


def ensure_directory_exists(path: Path) -> None:
    """
    Ensure a directory exists, creating it if necessary

    Args:
        path: Path to the directory
    """
    path.mkdir(parents=True, exist_ok=True)


async def save_upload_file(file: UploadFile, destination: Path) -> Path:
    """
    Save an uploaded file to the specified destination

    Args:
        file: FastAPI UploadFile object
        destination: Path where the file should be saved

    Returns:
        Path: The destination path where the file was saved

    Raises:
        IOError: If file cannot be saved
    """
    # Ensure parent directory exists
    destination.parent.mkdir(parents=True, exist_ok=True)

    # Save file asynchronously
    async with aiofiles.open(destination, 'wb') as f:
        while content := await file.read(1024 * 1024):  # Read 1MB chunks
            await f.write(content)

    return destination


async def get_file_hash(file_path: Path) -> str:
    """
    Calculate SHA-256 hash of a file

    Args:
        file_path: Path to the file

    Returns:
        str: SHA-256 hash in hexadecimal format

    Raises:
        FileNotFoundError: If file does not exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    sha256_hash = hashlib.sha256()

    async with aiofiles.open(file_path, 'rb') as f:
        while chunk := await f.read(8192):  # Read 8KB chunks
            sha256_hash.update(chunk)

    return sha256_hash.hexdigest()


def validate_file_type(filename: str, allowed_types: List[str]) -> bool:
    """
    Validate if a file has an allowed extension

    Args:
        filename: Name of the file
        allowed_types: List of allowed file extensions (e.g., ['.pdf', '.docx'])

    Returns:
        bool: True if file type is allowed, False otherwise
    """
    file_ext = Path(filename).suffix.lower()
    return file_ext in [ext.lower() for ext in allowed_types]


def get_mime_type(file_path: Path) -> str:
    """
    Get the MIME type of a file

    Args:
        file_path: Path to the file

    Returns:
        str: MIME type (e.g., 'application/pdf')
    """
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type or 'application/octet-stream'


def ensure_directory(path: Path) -> None:
    """
    Ensure a directory exists, creating it if necessary

    Args:
        path: Path to the directory
    """
    path.mkdir(parents=True, exist_ok=True)
