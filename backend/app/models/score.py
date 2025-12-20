"""
Score Model
"""

import enum
from sqlalchemy import Column, String, Enum, ForeignKey, Integer, Float, JSON, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base, generate_uuid


class ScoreType(str, enum.Enum):
    """Score type enum"""
    COMPLIANCE = "compliance"
    TECHNICAL = "technical"
    FINANCIAL = "financial"


class Score(Base):
    """Score model for bid evaluation scores"""

    __tablename__ = "scores"

    id = Column(String(36), primary_key=True, default=generate_uuid)

    bid_id = Column(String(36), ForeignKey("bids.id"), nullable=False, index=True)
    evaluation_id = Column(String(36), ForeignKey("evaluations.id"), nullable=False, index=True)

    score_type = Column(Enum(ScoreType), nullable=False, index=True)

    total_score = Column(Float, nullable=False)
    max_score = Column(Float, default=100.0, nullable=False)

    # Detailed breakdown
    breakdown = Column(JSON, default=dict, nullable=True)
    justification = Column(Text, nullable=True)
    ai_reasoning = Column(JSON, default=dict, nullable=True)

    is_qualified = Column(Boolean, default=False, nullable=False)

    scored_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    bid = relationship("Bid", back_populates="scores")
    evaluation = relationship("Evaluation", back_populates="scores")

    def __repr__(self):
        return f"<Score {self.score_type.value} for Bid {self.bid_id}>"
