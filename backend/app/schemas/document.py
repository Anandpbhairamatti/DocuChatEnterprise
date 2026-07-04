from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class DocumentBase(BaseModel):
    filename: str
    original_name: str
    file_type: str
    size_bytes: int
    department_id: Optional[UUID] = None
    document_metadata: Optional[Dict[str, Any]] = None
    visibility: str = "ORGANIZATION"

class DocumentCreate(DocumentBase):
    file_hash: str
    version: int = 1
    owner_id: UUID

class DocumentRead(DocumentBase):
    id: UUID
    file_hash: str
    version: int
    status: str
    uploaded_at: datetime
    owner_id: UUID

    class Config:
        from_attributes = True

class DocumentUpdate(BaseModel):
    status: Optional[str] = None
    document_metadata: Optional[Dict[str, Any]] = None
