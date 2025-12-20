"""
Admin Endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.dependencies import get_db
from app.core.auth import get_current_active_user, require_permission, Permission
from app.core.security import get_password_hash
from app.models.user import User
from app.models.department import Department
from app.models.audit_log import AuditLog
from app.schemas.auth import UserCreate, UserResponse

router = APIRouter()


@router.get("/users")
async def list_users(
    role: Optional[str] = None,
    department_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List users (admin only)"""
    query = select(User)

    # Apply filters
    if department_id:
        query = query.where(User.department_id == department_id)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(User.created_at.desc())

    result = await db.execute(query)
    users = result.scalars().all()

    return {
        "items": [
            {
                "id": u.id,
                "email": u.email,
                "name": u.name,
                "is_active": u.is_active,
                "created_at": u.created_at,
            }
            for u in users
        ],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit if total else 0,
    }


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new user (admin only)"""
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

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


@router.patch("/users/{user_id}")
async def update_user(
    user_id: str,
    name: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a user (admin only)"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if name is not None:
        user.name = name
    if is_active is not None:
        user.is_active = is_active

    await db.commit()
    await db.refresh(user)

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "is_active": user.is_active,
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a user (admin only)"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    await db.delete(user)
    await db.commit()

    return {"message": "User deleted"}


@router.get("/audit-logs")
async def list_audit_logs(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    actor_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List audit logs (admin only)"""
    query = select(AuditLog)

    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.where(AuditLog.entity_id == entity_id)
    if actor_id:
        query = query.where(AuditLog.actor_id == actor_id)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(AuditLog.created_at.desc())

    result = await db.execute(query)
    logs = result.scalars().all()

    return {
        "items": logs,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit if total else 0,
    }


@router.get("/departments")
async def list_departments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all departments"""
    result = await db.execute(select(Department).order_by(Department.name))
    departments = result.scalars().all()

    return {
        "items": [
            {
                "id": d.id,
                "name": d.name,
                "code": d.code,
                "ministry": d.ministry,
            }
            for d in departments
        ],
        "total": len(departments),
    }
