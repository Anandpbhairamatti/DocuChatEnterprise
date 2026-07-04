import os
import app.db.base # Register all SQLAlchemy models to prevent mapper errors
from celery import Task
from app.worker.celery_app import celery_app
from app.db.session import SessionLocal
from app.repositories.document_repo import document_repo
from app.document_processing.parsers import parser
from app.document_processing.chunking import structure_aware_chunking
from app.ai.vector_db import vector_db_provider
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class BaseTaskWithRetry(Task):
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3, 'countdown': 5}
    retry_backoff = True

def process_document_sync(document_id: str, file_path: str, file_type: str):
    db = SessionLocal()
    try:
        # 1. PROCESSING
        document_repo.update_status(db, document_id, "PROCESSING")
        
        # 2. EXTRACT TEXT
        document_repo.update_status(db, document_id, "OCR_RUNNING")
        text = parser.parse(file_path, file_type)
        if not text:
            raise ValueError("No text extracted from document")
        document_repo.update_status(db, document_id, "TEXT_EXTRACTED")
        
        # 3. CHUNKING
        chunks = structure_aware_chunking(text)
        db_chunks = document_repo.add_chunks(db, document_id, chunks)
        document_repo.update_status(db, document_id, "CHUNKED")
        
        # 4. EMBEDDINGS & VECTOR DB
        texts_to_embed = [c["text"] for c in chunks]
        
        # 5. VECTOR DB
        collection_name = "docuchat_collection"
        ids = [str(c.id) for c in db_chunks]
        
        doc = document_repo.get_by_id(db, document_id)
        
        metadatas = [{
            "document_id": str(document_id),
            "owner_id": str(doc.owner_id),
            "department_id": str(doc.department_id) if doc.department_id else "",
            "visibility": doc.visibility,
            "version": doc.version,
            **c.chunk_metadata
        } for c in db_chunks]
        
        vector_db_provider.add_documents(
            collection_name=collection_name,
            documents=texts_to_embed,
            metadatas=metadatas,
            ids=ids
        )
        
        document_repo.update_status(db, document_id, "INDEXED")
        
        # 6. COMPLETED
        document_repo.update_status(db, document_id, "COMPLETED")
        
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        document_repo.update_status(db, document_id, "FAILED")
        raise e
    finally:
        db.close()

@celery_app.task(bind=True, base=BaseTaskWithRetry)
def process_document_task(self, document_id: str, file_path: str, file_type: str):
    try:
        process_document_sync(document_id, file_path, file_type)
    except Exception as e:
        raise self.retry(exc=e)
