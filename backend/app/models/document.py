"""
Document Model
"""

from sqlalchemy import Column, String, Integer, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, generate_uuid


class Document(Base):
    """Document model for uploaded files"""

    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(50), nullable=False)  # tender, bid
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_hash = Column(String(64), nullable=True)  # SHA-256 hash

    # Extracted content
    extracted_data = Column(JSON, default=dict, nullable=True)
    # Note: extracted_text column doesn't exist in database yet
    # extracted_text = Column(Text, nullable=True)

    # Processing status
    processing_status = Column(String(50), default='pending', nullable=True)
    processing_error = Column(Text, nullable=True)

    uploaded_by_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Relationships
    uploader = relationship("User", foreign_keys=[uploaded_by_id])

    def __repr__(self):
        return f"<Document {self.filename}>"
