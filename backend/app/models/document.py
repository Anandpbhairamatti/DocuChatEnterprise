import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

# Import related models to ensure they are registered with SQLAlchemy
from app.models.user import User

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    filename = Column(String, nullable=False)
    original_name = Column(String, nullable=False)
    file_hash = Column(String, nullable=False, index=True) # SHA-256
    version = Column(Integer, default=1)
    file_type = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    status = Column(String, default="UPLOADED") # UPLOADED, QUEUED, PROCESSING, OCR_RUNNING, TEXT_EXTRACTED, CHUNKED, EMBEDDING_GENERATED, INDEXED, COMPLETED, FAILED
    document_metadata = Column(JSONB, nullable=True) # title, author, page count, language, timestamps
    visibility = Column(String, default="ORGANIZATION") # PRIVATE, DEPARTMENT, ORGANIZATION, RESTRICTED
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="documents")
    department = relationship("Department", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
