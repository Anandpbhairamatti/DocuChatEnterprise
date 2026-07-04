from typing import Optional, List
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.schemas.document import DocumentCreate, DocumentUpdate

class DocumentRepository:
    def create(self, db: Session, obj_in: DocumentCreate) -> Document:
        db_obj = Document(
            filename=obj_in.filename,
            original_name=obj_in.original_name,
            file_hash=obj_in.file_hash,
            version=obj_in.version,
            file_type=obj_in.file_type,
            size_bytes=obj_in.size_bytes,
            owner_id=obj_in.owner_id,
            department_id=obj_in.department_id,
            document_metadata=obj_in.document_metadata,
            status="UPLOADED"
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_id(self, db: Session, doc_id: UUID) -> Optional[Document]:
        return db.query(Document).filter(Document.id == doc_id).first()
        
    def get_by_hash(self, db: Session, file_hash: str) -> Optional[Document]:
        return db.query(Document).filter(Document.file_hash == file_hash).order_by(Document.version.desc()).first()

    def get_by_name_and_owner(self, db: Session, original_name: str, owner_id: UUID) -> Optional[Document]:
        return db.query(Document).filter(
            Document.original_name == original_name,
            Document.owner_id == owner_id
        ).order_by(Document.version.desc()).first()

    def delete_document(self, db: Session, doc_id: UUID) -> bool:
        doc = self.get_by_id(db, doc_id)
        if not doc:
            return False
            
        # 1. Delete chunks from ChromaDB
        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).all()
        chunk_ids = [str(c.id) for c in chunks]
        if chunk_ids:
            try:
                from app.ai.vector_db import vector_db_provider
                vector_db_provider.delete_documents("docuchat_collection", chunk_ids)
            except Exception as e:
                print(f"Failed to delete Chroma chunks: {e}")
                
        # 2. Delete physical file
        import os
        from app.core.config import settings
        file_path = os.path.join(settings.UPLOAD_DIR, doc.filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"Failed to delete physical file: {e}")
                
        # 3. Delete from DB (will cascade to chunks)
        db.delete(doc)
        db.commit()
        return True

    def update_status(self, db: Session, doc_id: UUID, status: str) -> Document:
        doc = self.get_by_id(db, doc_id)
        if doc:
            doc.status = status
            db.commit()
            db.refresh(doc)
        return doc
        
    def get_accessible_documents(self, db: Session, user) -> List[Document]:
        from sqlalchemy import or_, and_
        from app.core.permissions import has_permission, Permission
        
        if has_permission(user.role, Permission.READ_ALL_DOCUMENTS):
            # Admins can see everything in the dashboard to manage them
            return db.query(Document).order_by(Document.uploaded_at.desc()).all()
            
        conditions = [
            Document.owner_id == user.id,
            Document.visibility == "ORGANIZATION"
        ]
        
        if user.department_id:
            conditions.append(
                and_(
                    Document.visibility == "DEPARTMENT",
                    Document.department_id == user.department_id
                )
            )
            
        if has_permission(user.role, Permission.READ_RESTRICTED_DOCUMENTS):
            if has_permission(user.role, Permission.READ_ALL_DOCUMENTS):
                conditions.append(Document.visibility == "RESTRICTED")
            elif user.department_id:
                conditions.append(
                    and_(
                        Document.visibility == "RESTRICTED",
                        Document.department_id == user.department_id
                    )
                )
            
        return db.query(Document).filter(or_(*conditions)).order_by(Document.uploaded_at.desc()).all()
        
    def add_chunks(self, db: Session, doc_id: UUID, chunks: List[dict]):
        db_chunks = []
        for i, chunk in enumerate(chunks):
            db_chunk = DocumentChunk(
                document_id=doc_id,
                chunk_index=i,
                text_content=chunk["text"],
                chunk_metadata=chunk["metadata"]
            )
            db.add(db_chunk)
            db_chunks.append(db_chunk)
        db.commit()
        return db_chunks

document_repo = DocumentRepository()
