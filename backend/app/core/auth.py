"""
Authentication and Authorization
"""

from enum import Enum
from functools import wraps
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.core.security import verify_token
from app.models.user import User

# Security scheme
security = HTTPBearer()


class Permission(str, Enum):
    """Permission enum for RBAC"""
    VIEW_EVALUATIONS = "view_evaluations"
    CREATE_EVALUATION = "create_evaluation"
    START_EVALUATION = "start_evaluation"
    VIEW_RESULTS = "view_results"
    EXPORT_REPORTS = "export_reports"
    MANAGE_VENDORS = "manage_vendors"
    MANAGE_USERS = "manage_users"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    ADMIN = "admin"


# Role to permissions mapping
ROLE_PERMISSIONS = {
    "officer": [
        Permission.VIEW_EVALUATIONS,
        Permission.CREATE_EVALUATION,
        Permission.START_EVALUATION,
        Permission.VIEW_RESULTS,
        Permission.EXPORT_REPORTS,
        Permission.MANAGE_VENDORS,
    ],
    "evaluator": [
        Permission.VIEW_EVALUATIONS,
        Permission.VIEW_RESULTS,
    ],
    "admin": [
        Permission.ADMIN,
        Permission.VIEW_EVALUATIONS,
        Permission.CREATE_EVALUATION,
        Permission.START_EVALUATION,
        Permission.VIEW_RESULTS,
        Permission.EXPORT_REPORTS,
        Permission.MANAGE_VENDORS,
        Permission.MANAGE_USERS,
        Permission.VIEW_AUDIT_LOGS,
    ],
}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get the current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = verify_token(token, "access")

    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get the current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


def get_user_permissions(user: User) -> List[Permission]:
    """Get permissions for a user based on their role"""
    if user.role is None:
        return []

    role_name = user.role.name.lower()
    return ROLE_PERMISSIONS.get(role_name, [])


def require_permission(permission: Permission):
    """Decorator to require a specific permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_active_user), **kwargs):
            user_permissions = get_user_permissions(current_user)

            # Admin has all permissions
            if Permission.ADMIN in user_permissions:
                return await func(*args, current_user=current_user, **kwargs)

            # Check for required permission
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required: {permission.value}",
                )

            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


async def get_current_user_ws(
    token: str,
    db: AsyncSession,
) -> Optional[User]:
    """Get current user for WebSocket connections"""
    payload = verify_token(token, "access")

    if payload is None:
        return None

    user_id: str = payload.get("sub")
    if user_id is None:
        return None

    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
