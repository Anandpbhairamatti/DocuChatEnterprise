from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from app.models.chat import Chat
from app.models.message import Message
from app.models.ai_log import AILog
from app.schemas.chat import ChatCreate, MessageCreate

class ChatRepository:
    def create_chat(self, db: Session, obj_in: ChatCreate) -> Chat:
        db_obj = Chat(user_id=obj_in.user_id, title=obj_in.title)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
        
    def get_chat(self, db: Session, chat_id: UUID) -> Optional[Chat]:
        return db.query(Chat).filter(Chat.id == chat_id).first()
        
    def get_user_chats(self, db: Session, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Chat]:
        return db.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.updated_at.desc()).offset(skip).limit(limit).all()
        
    def delete_chat(self, db: Session, chat_id: UUID) -> bool:
        chat = self.get_chat(db, chat_id)
        if chat:
            db.delete(chat)
            db.commit()
            return True
        return False
        
    def add_message(self, db: Session, obj_in: MessageCreate) -> Message:
        # Convert citation objects to dicts for JSONB
        citations_dict = [c.model_dump() for c in obj_in.citations] if obj_in.citations else None
        
        db_obj = Message(
            chat_id=obj_in.chat_id,
            role=obj_in.role,
            content=obj_in.content,
            citations=citations_dict
        )
        db.add(db_obj)
        
        # Touch chat updated_at
        chat = self.get_chat(db, obj_in.chat_id)
        if chat:
            from datetime import datetime
            chat.updated_at = datetime.utcnow()
            
        db.commit()
        db.refresh(db_obj)
        return db_obj
        
    def get_chat_history(self, db: Session, chat_id: UUID, limit: int = 5) -> List[Message]:
        return db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at.desc()).limit(limit).all()[::-1]

    def get_all_chat_messages(self, db: Session, chat_id: UUID) -> List[Message]:
        return db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at.asc()).all()

    def create_ai_log(self, db: Session, **kwargs) -> AILog:
        db_obj = AILog(**kwargs)
        db.add(db_obj)
        db.commit()
        return db_obj

chat_repo = ChatRepository()
