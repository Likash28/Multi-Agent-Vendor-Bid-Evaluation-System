"""
Vendor Service
Handles vendor management and bid history
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import math

from app.models.vendor import Vendor
from app.models.bid import Bid
from app.repositories.vendor_repository import vendor_repository
from app.utils.validators import validate_gstin, validate_pan


class VendorService:
    """Service for vendor management"""

    def __init__(self):
        self.vendor_repo = vendor_repository

    async def get_or_create_vendor(
        self,
        db: AsyncSession,
        vendor_data: Dict[str, Any]
    ) -> Vendor:
        """
        Get existing vendor or create new one

        Looks up vendor by GSTIN, PAN, or registration number.
        Creates new vendor if not found.

        Args:
            db: Database session
            vendor_data: Vendor data dictionary

        Returns:
            Vendor instance (existing or newly created)

        Raises:
            HTTPException: If validation fails
        """
        # Validate GSTIN if provided
        gstin = vendor_data.get("gstin")
        if gstin:
            if not validate_gstin(gstin):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid GSTIN format"
                )

            # Check if vendor exists by GSTIN
            existing = await self.vendor_repo.get_by_gstin(db, gstin)
            if existing:
                return existing

        # Validate PAN if provided
        pan = vendor_data.get("pan")
        if pan:
            if not validate_pan(pan):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid PAN format"
                )

            # Check if vendor exists by PAN
            existing = await self.vendor_repo.get_by_pan(db, pan)
            if existing:
                return existing

        # Check by registration number
        registration_no = vendor_data.get("registration_no")
        if registration_no:
            existing = await self.vendor_repo.get_by_registration_no(db, registration_no)
            if existing:
                return existing

        # Check by name (exact match)
        name = vendor_data.get("name")
        if name:
            existing = await self.vendor_repo.get_by_name(db, name)
            if existing:
                return existing

        # Create new vendor
        vendor = await self.vendor_repo.create(db, vendor_data)
        return vendor

    async def get_vendor(
        self,
        db: AsyncSession,
        vendor_id: str
    ) -> Vendor:
        """
        Get vendor by ID

        Args:
            db: Database session
            vendor_id: Vendor ID

        Returns:
            Vendor instance

        Raises:
            HTTPException: If vendor not found
        """
        vendor = await self.vendor_repo.get(db, vendor_id)

        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found"
            )

        return vendor

    async def list_vendors(
        self,
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        verified_only: bool = False
    ) -> tuple[List[Vendor], int, int]:
        """
        List vendors with pagination

        Args:
            db: Database session
            page: Page number (1-indexed)
            limit: Items per page
            verified_only: Only return verified vendors

        Returns:
            Tuple of (vendors, total_count, total_pages)
        """
        # Calculate skip
        skip = (page - 1) * limit

        # Get vendors
        if verified_only:
            vendors = await self.vendor_repo.get_verified_vendors(db, skip, limit)
            total = await self.vendor_repo.count(db, is_verified=True)
        else:
            vendors = await self.vendor_repo.get_multi(db, skip, limit)
            total = await self.vendor_repo.count(db)

        # Calculate total pages
        total_pages = math.ceil(total / limit) if total > 0 else 1

        return vendors, total, total_pages

    async def search_vendors(
        self,
        db: AsyncSession,
        query: str,
        page: int = 1,
        limit: int = 20
    ) -> tuple[List[Vendor], int]:
        """
        Search vendors by name

        Args:
            db: Database session
            query: Search query
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Tuple of (vendors, total_count)
        """
        skip = (page - 1) * limit
        vendors = await self.vendor_repo.search_by_name(db, query, skip, limit)

        # For simplicity, return found count (not exact total)
        # In production, you'd want a separate count query
        total = len(vendors)

        return vendors, total

    async def get_vendor_bid_history(
        self,
        db: AsyncSession,
        vendor_id: str,
        page: int = 1,
        limit: int = 20
    ) -> tuple[List[Bid], int]:
        """
        Get bid history for a vendor

        Args:
            db: Database session
            vendor_id: Vendor ID
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Tuple of (bids, total_count)

        Raises:
            HTTPException: If vendor not found
        """
        # Verify vendor exists
        await self.get_vendor(db, vendor_id)

        # Calculate skip
        skip = (page - 1) * limit

        # Get bids
        bids = await self.vendor_repo.get_vendor_bids(db, vendor_id, skip, limit)

        # For simplicity, return found count
        total = len(bids)

        return bids, total

    async def update_vendor(
        self,
        db: AsyncSession,
        vendor_id: str,
        update_data: Dict[str, Any]
    ) -> Vendor:
        """
        Update vendor information

        Args:
            db: Database session
            vendor_id: Vendor ID
            update_data: Data to update

        Returns:
            Updated vendor instance

        Raises:
            HTTPException: If vendor not found or validation fails
        """
        vendor = await self.get_vendor(db, vendor_id)

        # Validate GSTIN if being updated
        if "gstin" in update_data and update_data["gstin"]:
            if not validate_gstin(update_data["gstin"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid GSTIN format"
                )

        # Validate PAN if being updated
        if "pan" in update_data and update_data["pan"]:
            if not validate_pan(update_data["pan"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid PAN format"
                )

        # Update vendor
        vendor = await self.vendor_repo.update(db, vendor, update_data)

        return vendor

    async def verify_vendor(
        self,
        db: AsyncSession,
        vendor_id: str
    ) -> Vendor:
        """
        Mark vendor as verified

        Args:
            db: Database session
            vendor_id: Vendor ID

        Returns:
            Updated vendor instance

        Raises:
            HTTPException: If vendor not found
        """
        return await self.update_vendor(db, vendor_id, {"is_verified": True})


# Singleton instance
vendor_service = VendorService()
