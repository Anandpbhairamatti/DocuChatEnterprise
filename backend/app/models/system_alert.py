import uuid
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db.base_class import Base

class SystemAlert(Base):
    __tablename__ = "system_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    severity = Column(String, nullable=False) # "INFO", "WARNING", "ERROR", "CRITICAL"
    source = Column(String, nullable=False) # e.g. "Celery Worker", "PostgreSQL", "Groq API"
    message = Column(String, nullable=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
