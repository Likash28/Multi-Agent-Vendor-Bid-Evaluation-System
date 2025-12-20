"""
Security utilities for password hashing and JWT tokens
"""

import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
from jose import JWTError, jwt

from app.config import settings


def _prepare_password(password: str) -> bytes:
    """
    Prepare password for bcrypt hashing.
    Bcrypt has a 72-byte limit, so we hash longer passwords with SHA256 first.
    This ensures compatibility while maintaining security.
    """
    password_bytes = password.encode('utf-8')
    
    # If password is longer than 72 bytes, hash it with SHA256 first
    if len(password_bytes) > 72:
        # Hash with SHA256 to get a fixed 64-character hex string (32 bytes)
        sha256_hash = hashlib.sha256(password_bytes).hexdigest()
        return sha256_hash.encode('utf-8')
    
    return password_bytes


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        prepared_password = _prepare_password(plain_password)
        # Try with prepared password first
        if bcrypt.checkpw(prepared_password, hashed_password.encode('utf-8')):
            return True
    except Exception:
        pass
    
    # Fallback: try with original password for backward compatibility
    try:
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) <= 72:
            return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    except Exception:
        pass
    
    return False


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    prepared_password = _prepare_password(password)
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(prepared_password, salt)
    return hashed.decode('utf-8')


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
