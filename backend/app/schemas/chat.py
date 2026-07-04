from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class Citation(BaseModel):
    chunk_id: str
    document_id: str
    page_number: Optional[int] = None
    snippet: str

class MessageBase(BaseModel):
    role: str # "user" or "ai"
    content: str
    citations: Optional[List[Citation]] = None

class MessageCreate(MessageBase):
    chat_id: UUID

class MessageRead(MessageBase):
    id: UUID
    chat_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatBase(BaseModel):
    title: Optional[str] = None

class ChatCreate(ChatBase):
    user_id: UUID

class ChatRead(ChatBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[MessageRead] = []
    
    class Config:
        from_attributes = True

class QuestionRequest(BaseModel):
    query: str
    chat_id: Optional[UUID] = None # If None, creates a new chat
