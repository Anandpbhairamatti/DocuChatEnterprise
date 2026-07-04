from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
from app.models.document import Document
from app.models.ai_log import AILog
from app.models.chat import Chat
from app.models.message import Message

class AnalyticsService:
    def get_overview(self, db: Session) -> dict:
        total_users = db.query(func.count(User.id)).scalar()
        total_documents = db.query(func.count(Document.id)).scalar()
        total_storage_bytes = db.query(func.sum(Document.size_bytes)).scalar() or 0
        
        # AI Metrics
        avg_response_time = db.query(func.avg(AILog.response_time_ms)).scalar() or 0
        total_prompt_tokens = db.query(func.sum(AILog.prompt_tokens)).scalar() or 0
        total_completion_tokens = db.query(func.sum(AILog.completion_tokens)).scalar() or 0
        
        # Rough estimated cost (Groq Llama 3 8B pricing as example)
        # $0.05 per 1M prompt tokens, $0.08 per 1M completion tokens
        est_cost = (total_prompt_tokens / 1_000_000 * 0.05) + (total_completion_tokens / 1_000_000 * 0.08)

        total_chats = db.query(func.count(Chat.id)).scalar()
        total_messages = db.query(func.count(Message.id)).scalar()
        
        return {
            "users": {
                "total": total_users
            },
            "documents": {
                "total": total_documents,
                "storage_bytes": total_storage_bytes
            },
            "ai": {
                "avg_response_time_ms": round(avg_response_time, 2),
                "total_prompt_tokens": total_prompt_tokens,
                "total_completion_tokens": total_completion_tokens,
                "estimated_cost_usd": round(est_cost, 4)
            },
            "activity": {
                "total_chats": total_chats,
                "total_messages": total_messages
            }
        }

analytics_service = AnalyticsService()
