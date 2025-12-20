"""
Authentication Schemas
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=2, max_length=255)
    department_id: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response"""
    id: str
    email: str
    name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=6)
