"""
Authentication Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    create_password_reset_token,
    verify_password_reset_token,
)
from app.core.auth import get_current_active_user
from app.models.user import User
from app.schemas.auth import (
    UserCreate,
    UserLogin,
    TokenResponse,
    UserResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user"""
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    # Create new user
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        name=user_data.name,
        department_id=user_data.department_id,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Login and get access token"""
    # Find user
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using refresh token"""
    payload = verify_token(request.refresh_token, "refresh")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_id = payload.get("sub")

    # Verify user still exists and is active
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
):
    """Logout user (client should discard tokens)"""
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
):
    """Get current user information"""
    return current_user


@router.post("/forgot-password")
async def forgot_password(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """Request password reset"""
    # Find user
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    # Always return success to prevent email enumeration
    if user:
        # In production, send email with reset token
        token = create_password_reset_token(user.email)
        # TODO: Send email with token
        print(f"Password reset token for {user.email}: {token}")

    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
    request: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
):
    """Reset password using token"""
    email = verify_password_reset_token(request.token)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Find user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update password
    user.password_hash = get_password_hash(request.new_password)
    await db.commit()

    return {"message": "Password reset successful"}
