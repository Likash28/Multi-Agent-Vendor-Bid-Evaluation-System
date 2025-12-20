"""
Bid Model
"""

import enum
from sqlalchemy import Column, String, Enum, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship

from app.models.base import Base, generate_uuid


class BidStatus(str, enum.Enum):
    """Bid status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"


class Bid(Base):
    """Bid model for vendor bids"""

    __tablename__ = "bids"

    id = Column(String(36), primary_key=True, default=generate_uuid)

    evaluation_id = Column(String(36), ForeignKey("evaluations.id"), nullable=False, index=True)
    vendor_id = Column(String(36), ForeignKey("vendors.id"), nullable=False, index=True)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=True)

    # Bid amount stored in paisa (smallest unit)
    bid_amount = Column(Integer, nullable=True)

    submitted_at = Column(DateTime, nullable=True)
    status = Column(Enum(BidStatus), default=BidStatus.PENDING, nullable=False)

    # Relationships
    evaluation = relationship("Evaluation", back_populates="bids", foreign_keys=[evaluation_id])
    vendor = relationship("Vendor", back_populates="bids")
    document = relationship("Document", foreign_keys=[document_id])
    scores = relationship("Score", back_populates="bid")

    def __repr__(self):
        return f"<Bid {self.id} by Vendor {self.vendor_id}>"
