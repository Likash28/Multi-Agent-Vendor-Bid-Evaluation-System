"""
Vendor Repository
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.vendor import Vendor
from app.models.bid import Bid
from app.repositories.base import BaseRepository


class VendorRepository(BaseRepository[Vendor, dict, dict]):
    """Repository for Vendor model operations"""

    def __init__(self):
        super().__init__(Vendor)

    async def get_by_gstin(self, db: AsyncSession, gstin: str) -> Optional[Vendor]:
        """
        Get vendor by GSTIN

        Args:
            db: Database session
            gstin: GST Identification Number

        Returns:
            Vendor instance or None if not found
        """
        result = await db.execute(select(Vendor).where(Vendor.gstin == gstin))
        return result.scalar_one_or_none()

    async def get_by_pan(self, db: AsyncSession, pan: str) -> Optional[Vendor]:
        """
        Get vendor by PAN

        Args:
            db: Database session
            pan: Permanent Account Number

        Returns:
            Vendor instance or None if not found
        """
        result = await db.execute(select(Vendor).where(Vendor.pan == pan))
        return result.scalar_one_or_none()

    async def get_by_registration_no(
        self,
        db: AsyncSession,
        registration_no: str
    ) -> Optional[Vendor]:
        """
        Get vendor by registration number

        Args:
            db: Database session
            registration_no: Vendor registration number

        Returns:
            Vendor instance or None if not found
        """
        result = await db.execute(
            select(Vendor).where(Vendor.registration_no == registration_no)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Vendor]:
        """
        Get vendor by exact name match

        Args:
            db: Database session
            name: Vendor name

        Returns:
            Vendor instance or None if not found
        """
        result = await db.execute(select(Vendor).where(Vendor.name == name))
        return result.scalar_one_or_none()

    async def search_by_name(
        self,
        db: AsyncSession,
        name_pattern: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Vendor]:
        """
        Search vendors by name pattern

        Args:
            db: Database session
            name_pattern: Name pattern to search (case-insensitive)
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of matching vendors
        """
        result = await db.execute(
            select(Vendor)
            .where(Vendor.name.ilike(f"%{name_pattern}%"))
            .order_by(Vendor.name)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_verified_vendors(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Vendor]:
        """
        Get verified vendors only

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of verified vendors
        """
        result = await db.execute(
            select(Vendor)
            .where(Vendor.is_verified == True)
            .order_by(Vendor.name)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_vendor_bids(
        self,
        db: AsyncSession,
        vendor_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Bid]:
        """
        Get bid history for a vendor

        Args:
            db: Database session
            vendor_id: Vendor ID
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of bids
        """
        result = await db.execute(
            select(Bid)
            .where(Bid.vendor_id == vendor_id)
            .order_by(Bid.submitted_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


# Singleton instance
vendor_repository = VendorRepository()
