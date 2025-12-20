"""
Role Model
"""

from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import relationship

from app.models.base import Base, generate_uuid


class Role(Base):
    """Role model for RBAC"""

    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(50), unique=True, nullable=False)
    permissions = Column(JSON, default=list, nullable=False)

    # Relationships
    users = relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role {self.name}>"
