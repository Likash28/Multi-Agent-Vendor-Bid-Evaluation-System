"""
Department Model
"""

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.models.base import Base, generate_uuid


class Department(Base):
    """Department model for organizational hierarchy"""

    __tablename__ = "departments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    ministry = Column(String(255), nullable=True)

    # Relationships
    users = relationship("User", back_populates="department")

    def __repr__(self):
        return f"<Department {self.name}>"
