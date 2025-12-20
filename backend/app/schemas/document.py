"""
Document Schemas
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class DocumentResponse(BaseModel):
    """Schema for document response"""
    id: str
    filename: str
    file_type: str
    file_size: int
    mime_type: str
    extracted_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True
