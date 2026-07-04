import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
from app.db.base_class import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action = Column(String, nullable=False) # e.g. "USER_CREATED", "DOCUMENT_DELETED", "ROLE_CHANGED"
    target_resource_id = Column(String, nullable=True)
    target_resource_type = Column(String, nullable=True) # e.g. "User", "Document", "SystemConfig"
    details = Column(JSONB, nullable=True) # Before/After states
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
