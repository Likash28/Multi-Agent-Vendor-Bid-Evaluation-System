"""
SQLAlchemy Base Model
"""

from datetime import datetime
from typing import Any
import uuid
from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """Base model class with common fields"""

    id: Any

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name"""
        return cls.__name__.lower() + "s"

    # Common timestamp fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


def generate_uuid() -> str:
    """Generate a new UUID string"""
    return str(uuid.uuid4())
