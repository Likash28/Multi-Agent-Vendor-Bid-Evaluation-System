"""
Authentication Service
Handles user registration, login, and token management
"""

from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.auth import UserCreate, UserResponse, TokenResponse
from app.repositories.user_repository import user_repository
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)


class AuthService:
    """Service for authentication and user management"""

    def __init__(self):
        self.user_repo = user_repository

    async def register_user(
        self,
        db: AsyncSession,
        user_data: UserCreate
    ) -> User:
        """
        Register a new user

        Args:
            db: Database session
            user_data: User registration data

        Returns:
            Created user instance

        Raises:
            HTTPException: If email already exists
        """
        # Check if email already exists
        if await self.user_repo.email_exists(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash password
        password_hash = get_password_hash(user_data.password)

        # Create user
        user_dict = user_data.model_dump(exclude={"password"})
        user_dict["password_hash"] = password_hash

        user = await self.user_repo.create(db, user_dict)

        return user

    async def authenticate_user(
        self,
        db: AsyncSession,
        email: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate a user with email and password

        Args:
            db: Database session
            email: User email
            password: User password

        Returns:
            User instance if authenticated, None otherwise
        """
        # Get user by email
        user = await self.user_repo.get_active_user_by_email(db, email)

        if not user:
            return None

        # Verify password
        if not verify_password(password, user.password_hash):
            return None

        return user

    def create_user_tokens(self, user: User) -> TokenResponse:
        """
        Create access and refresh tokens for a user

        Args:
            user: User instance

        Returns:
            TokenResponse with tokens and user data
        """
        # Create token payload
        token_data = {
            "sub": user.id,
            "email": user.email,
        }

        # Create tokens
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        # Create user response
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            created_at=user.created_at,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_response,
        )

    async def refresh_access_token(
        self,
        db: AsyncSession,
        refresh_token: str
    ) -> TokenResponse:
        """
        Refresh access token using refresh token

        Args:
            db: Database session
            refresh_token: Refresh token

        Returns:
            New TokenResponse with fresh tokens

        Raises:
            HTTPException: If refresh token is invalid
        """
        # Verify refresh token
        payload = verify_token(refresh_token, token_type="refresh")

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Get user
        user_id = payload.get("sub")
        user = await self.user_repo.get(db, user_id)

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Create new tokens
        return self.create_user_tokens(user)

    def invalidate_refresh_token(self, token: str) -> None:
        """
        Invalidate a refresh token (logout)

        Note: In a production system, you would typically:
        1. Store refresh tokens in database with expiry
        2. Maintain a blacklist of invalidated tokens
        3. Use Redis for token blacklist with TTL

        For now, this is a placeholder for token invalidation logic.

        Args:
            token: Refresh token to invalidate
        """
        # TODO: Implement token blacklist in production
        # This could be stored in Redis with the token's remaining TTL
        pass

    async def get_current_user(
        self,
        db: AsyncSession,
        access_token: str
    ) -> User:
        """
        Get current user from access token

        Args:
            db: Database session
            access_token: JWT access token

        Returns:
            User instance

        Raises:
            HTTPException: If token is invalid or user not found
        """
        # Verify token
        payload = verify_token(access_token, token_type="access")

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user
        user_id = payload.get("sub")
        user = await self.user_repo.get(db, user_id)

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user


# Singleton instance
auth_service = AuthService()
