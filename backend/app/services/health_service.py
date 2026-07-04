import groq
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.ai.vector_db import vector_db_provider
from app.worker.celery_app import celery_app

class HealthService:
    def check_health(self, db: Session) -> dict:
        health = {
            "status": "ok",
            "postgres": "unknown",
            "redis": "unknown",
            "celery": "unknown",
            "chromadb": "unknown",
            "groq_api": "unknown"
        }
        
        # 1. Check DB
        try:
            db.execute(text("SELECT 1"))
            health["postgres"] = "ok"
        except Exception:
            health["postgres"] = "error"
            health["status"] = "error"
            
        # 2. Check Celery / Redis
        try:
            inspector = celery_app.control.inspect()
            stats = inspector.stats()
            if stats:
                health["celery"] = "ok"
                health["redis"] = "ok" # Celery uses Redis as broker here
            else:
                health["celery"] = "error (no workers)"
                health["status"] = "error"
        except Exception:
            health["celery"] = "error"
            health["redis"] = "error"
            health["status"] = "error"
            
        # 3. Check ChromaDB
        try:
            # simple ping equivalent
            vector_db_provider.client.list_collections()
            health["chromadb"] = "ok"
        except Exception:
            health["chromadb"] = "error"
            health["status"] = "error"
            
        # 4. Check Groq API
        try:
            client = groq.Groq(api_key=settings.GROQ_API_KEY)
            client.models.list()
            health["groq_api"] = "ok"
        except Exception:
            health["groq_api"] = "error"
            health["status"] = "error"
            
        return health

health_service = HealthService()
