import sys
sys.path.append(r"C:\Users\Administrator\OneDrive\Desktop\CQA\backend")
import app.db.base # Register all models
from app.db.session import SessionLocal
from app.models.document import Document
from app.worker.tasks import process_document_task

db = SessionLocal()
docs = db.query(Document).filter(Document.status == "QUEUED").all()
for doc in docs:
    print(f"Re-triggering doc {doc.id}")
    process_document_task.delay(str(doc.id), f".storage/documents/{doc.filename}", doc.file_type)
print(f"Re-triggered {len(docs)} documents.")
