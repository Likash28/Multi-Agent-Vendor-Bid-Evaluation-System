"""
Vendor Model
"""

from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, generate_uuid


class Vendor(Base):
    """Vendor model for bid submitters"""

    __tablename__ = "vendors"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, index=True)
    registration_no = Column(String(100), unique=True, nullable=True)
    gstin = Column(String(15), unique=True, nullable=True)
    pan = Column(String(10), nullable=True)

    address = Column(Text, nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)

    is_verified = Column(Boolean, default=False, nullable=False)

    # Relationships
    bids = relationship("Bid", back_populates="vendor")

    def __repr__(self):
        return f"<Vendor {self.name}>"
