"""
Security utilities for password hashing and JWT tokens
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow(),
    })

    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow(),
    })

    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token

    Args:
        token: JWT token string
        token_type: Expected token type ("access" or "refresh")

    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Verify token type
        if payload.get("type") != token_type:
            return None

        return payload

    except JWTError:
        return None


def create_password_reset_token(email: str) -> str:
    """Create a password reset token"""
    data = {"email": email}
    expire = datetime.utcnow() + timedelta(hours=1)

    to_encode = {
        **data,
        "exp": expire,
        "type": "password_reset",
        "iat": datetime.utcnow(),
    }

    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token and return the email

    Returns:
        Email address or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        if payload.get("type") != "password_reset":
            return None

        return payload.get("email")

    except JWTError:
        return None
