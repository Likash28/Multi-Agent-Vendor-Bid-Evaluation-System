"""
Vendor Endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.dependencies import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.vendor import Vendor
from app.models.bid import Bid
from app.schemas.vendor import VendorResponse, VendorListResponse
from app.services.vendor_service import vendor_service
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class VendorCreate(BaseModel):
    """Schema for creating a vendor"""
    name: str
    gstin: Optional[str] = None
    registration_no: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None


@router.get("", response_model=VendorListResponse)
async def list_vendors(
    search: Optional[str] = None,
    verified: Optional[bool] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List vendors with search and filters"""
    query = select(Vendor)

    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Vendor.name.ilike(search_term),
                Vendor.gstin.ilike(search_term),
                Vendor.registration_no.ilike(search_term),
            )
        )

    if verified is not None:
        query = query.where(Vendor.is_verified == verified)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Vendor.name)

    result = await db.execute(query)
    vendors = result.scalars().all()

    return {
        "items": vendors,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit if total else 0,
    }


@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(
    vendor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get vendor by ID"""
    result = await db.execute(
        select(Vendor).where(Vendor.id == vendor_id)
    )
    vendor = result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found",
        )

    return vendor


@router.post("", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    vendor_data: VendorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create or get existing vendor (get_or_create pattern)"""
    vendor = await vendor_service.get_or_create_vendor(
        db,
        vendor_data.model_dump()
    )
    # Commit transaction to ensure vendor is saved
    await db.commit()
    await db.refresh(vendor)
    return vendor


@router.get("/{vendor_id}/history")
async def get_vendor_history(
    vendor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get vendor bid history"""
    # Verify vendor exists
    result = await db.execute(
        select(Vendor).where(Vendor.id == vendor_id)
    )
    vendor = result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found",
        )

    # Get bids
    bids_result = await db.execute(
        select(Bid).where(Bid.vendor_id == vendor_id).order_by(Bid.submitted_at.desc())
    )
    bids = bids_result.scalars().all()

    return {
        "vendor_id": vendor_id,
        "vendor_name": vendor.name,
        "total_bids": len(bids),
        "bids": [
            {
                "id": bid.id,
                "evaluation_id": bid.evaluation_id,
                "status": bid.status.value,
                "submitted_at": bid.submitted_at,
            }
            for bid in bids
        ],
    }
