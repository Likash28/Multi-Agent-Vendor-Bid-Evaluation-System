"""
User Model
"""

from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base, generate_uuid


class User(Base):
    """User model for authentication and authorization"""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)

    department_id = Column(String(36), ForeignKey("departments.id"), nullable=True)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    department = relationship("Department", back_populates="users")
    role = relationship("Role", back_populates="users")
    evaluations = relationship("Evaluation", back_populates="created_by_user", foreign_keys="Evaluation.created_by")

    def __repr__(self):
        return f"<User {self.email}>"
