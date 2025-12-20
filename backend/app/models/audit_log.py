"""
Audit Log Model
"""

from sqlalchemy import Column, String, ForeignKey, JSON, Text

from app.models.base import Base, generate_uuid


class AuditLog(Base):
    """Audit log model for tracking changes"""

    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)

    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(36), nullable=False, index=True)
    action = Column(String(50), nullable=False)  # created, updated, deleted, etc.

    actor_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    changes = Column(JSON, default=dict, nullable=True)
    details = Column(Text, nullable=True)

    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.entity_type}/{self.entity_id}>"
