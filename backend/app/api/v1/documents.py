import os
import hashlib
import shutil
from typing import Any, List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.api import dependencies
from app.models.user import User
from app.repositories.document_repo import document_repo
from app.schemas.document import DocumentCreate, DocumentRead
from app.core.config import settings
from app.worker.tasks import process_document_sync
from app.core.permissions import has_permission, Permission

router = APIRouter()

def get_file_hash(file: UploadFile) -> str:
    sha256_hash = hashlib.sha256()
    file.file.seek(0)
    for byte_block in iter(lambda: file.file.read(4096), b""):
        sha256_hash.update(byte_block)
    file.file.seek(0)
    return sha256_hash.hexdigest()

@router.get("/", response_model=List[DocumentRead])
def get_user_documents(
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user)
) -> Any:
    return document_repo.get_accessible_documents(db, current_user)

from fastapi import Form
from app.repositories.audit_repo import audit_repo

@router.post("/upload", response_model=DocumentRead, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    visibility: str = Form("ORGANIZATION"),
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user)
) -> Any:
    """
    Upload a document. Returns 202 Accepted while processing happens in the background.
    """
    valid_visibilities = ["PRIVATE", "DEPARTMENT", "ORGANIZATION", "RESTRICTED"]
    if visibility not in valid_visibilities:
        raise HTTPException(status_code=400, detail="Invalid visibility level")
        
    if visibility == "RESTRICTED" and not has_permission(current_user.role, Permission.UPLOAD_RESTRICTED_DOCUMENT):
        audit_repo.create_log(
            db, 
            admin_id=current_user.id, 
            action="UPLOAD_DENIED_RESTRICTED", 
            target_resource_type="Document",
            details={"filename": file.filename, "role": current_user.role}
        )
        raise HTTPException(status_code=403, detail="Only Admins and Managers can upload RESTRICTED documents")

    # 1. Version Check & Deduplication
    file_hash = get_file_hash(file)
    existing_doc = document_repo.get_by_name_and_owner(db, file.filename, current_user.id)
    
    version = 1
    if existing_doc:
        if existing_doc.file_hash == file_hash:
            raise HTTPException(status_code=400, detail="This exact document has already been uploaded.")
            
        version = existing_doc.version + 1
        # Delete old version to prevent AI context bloat
        document_repo.delete_document(db, existing_doc.id)
            
    # 2. Save file locally
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    saved_filename = f"{file_hash}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, saved_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    size_bytes = os.path.getsize(file_path)
    
    metadata = {
        "title": file.filename,
        "author": "Unknown", 
        "size_bytes": size_bytes,
        "content_type": file.content_type
    }
    
    # 3. Create Document DB Entry
    doc_in = DocumentCreate(
        filename=saved_filename,
        original_name=file.filename,
        file_hash=file_hash,
        version=version,
        file_type=file.content_type or "application/octet-stream",
        size_bytes=size_bytes,
        owner_id=current_user.id,
        department_id=current_user.department_id,
        document_metadata=metadata,
        visibility=visibility
    )
    
    document = document_repo.create(db, doc_in)
    
    audit_repo.create_log(
        db, 
        admin_id=current_user.id, 
        action="DOCUMENT_UPLOADED", 
        target_resource_id=str(document.id),
        target_resource_type="Document",
        details={"visibility": visibility, "size_bytes": size_bytes}
    )
    
    # 4. Dispatch Background Task
    document_repo.update_status(db, document.id, "QUEUED")
    background_tasks.add_task(process_document_sync, str(document.id), file_path, document.file_type)
    
    return document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: str,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user)
):
    from uuid import UUID
    try:
        doc_uuid = UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
        
    doc = document_repo.get_by_id(db, doc_uuid)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    if doc.owner_id != current_user.id and not has_permission(current_user.role, Permission.DELETE_ANY_DOCUMENT):
        raise HTTPException(status_code=403, detail="Not authorized to delete this document")
        
    success = document_repo.delete_document(db, doc_uuid)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete document")
        
    audit_repo.create_log(
        db, 
        admin_id=current_user.id, 
        action="DOCUMENT_DELETED", 
        target_resource_id=str(doc.id),
        target_resource_type="Document",
        details={"filename": doc.original_name}
    )
    
    return None
