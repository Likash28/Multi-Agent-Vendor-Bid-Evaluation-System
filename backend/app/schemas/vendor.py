"""
Vendor Schemas
"""

from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class VendorResponse(BaseModel):
    """Schema for vendor response"""
    id: str
    name: str
    registration_no: Optional[str] = None
    gstin: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class VendorListResponse(BaseModel):
    """Schema for vendor list response"""
    items: List[VendorResponse]
    total: int
    page: int
    pages: int
