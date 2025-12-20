"""
Evaluation Model
"""

import enum
from sqlalchemy import Column, String, Enum, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship

from app.models.base import Base, generate_uuid


class EvaluationStatus(str, enum.Enum):
    """Evaluation status enum"""
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EvaluationMethod(str, enum.Enum):
    """Evaluation method enum"""
    L1 = "l1"  # Lowest Price
    QCBS = "qcbs"  # Quality & Cost Based Selection
    TWO_STAGE = "two_stage"  # Two-Stage Bidding


class Evaluation(Base):
    """Evaluation model for bid evaluation process"""

    __tablename__ = "evaluations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    reference_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)

    tender_document_id = Column(String(36), ForeignKey("documents.id"), nullable=True)
    department_id = Column(String(36), ForeignKey("departments.id"), nullable=True)

    # Configuration stored as JSON
    config = Column(JSON, nullable=False, default=dict)
    # {
    #   "method": "qcbs",
    #   "technical_weight": 70,
    #   "financial_weight": 30,
    #   "qualification_threshold": 75,
    #   "enable_compliance_check": true,
    #   "enable_justifications": true,
    #   "enable_cartel_detection": false
    # }

    status = Column(Enum(EvaluationStatus), default=EvaluationStatus.DRAFT, nullable=False)

    # Processing metadata
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)
    processing_logs = Column(JSON, default=list, nullable=True)

    # Results summary
    results_summary = Column(JSON, nullable=True)
    winner_bid_id = Column(String(36), ForeignKey("bids.id"), nullable=True)

    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)

    # Relationships
    tender_document = relationship("Document", foreign_keys=[tender_document_id])
    bids = relationship("Bid", back_populates="evaluation", foreign_keys="Bid.evaluation_id")
    scores = relationship("Score", back_populates="evaluation")
    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="evaluations")
    winner_bid = relationship("Bid", foreign_keys=[winner_bid_id])

    def __repr__(self):
        return f"<Evaluation {self.reference_id}>"
