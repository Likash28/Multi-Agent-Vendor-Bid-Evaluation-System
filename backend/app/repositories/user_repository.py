"""
User Repository
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.auth import UserCreate


class UserRepository(BaseRepository[User, UserCreate, dict]):
    """Repository for User model operations"""

    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """
        Get user by email address

        Args:
            db: Database session
            email: User email

        Returns:
            User instance or None if not found
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_active_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """
        Get active user by email address

        Args:
            db: Database session
            email: User email

        Returns:
            User instance or None if not found or inactive
        """
        result = await db.execute(
            select(User).where(User.email == email, User.is_active == True)
        )
        return result.scalar_one_or_none()

    async def email_exists(self, db: AsyncSession, email: str) -> bool:
        """
        Check if email already exists

        Args:
            db: Database session
            email: Email to check

        Returns:
            True if email exists, False otherwise
        """
        result = await db.execute(select(User.id).where(User.email == email))
        return result.scalar_one_or_none() is not None


# Singleton instance
user_repository = UserRepository()
