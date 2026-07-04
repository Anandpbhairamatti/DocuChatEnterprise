from sqlalchemy.orm import Session
from uuid import UUID
from app.models.audit_log import AuditLog
from typing import Optional, Dict, Any

class AuditRepository:
    def create_log(self, db: Session, admin_id: UUID, action: str, 
                   target_resource_id: Optional[str] = None,
                   target_resource_type: Optional[str] = None,
                   details: Optional[Dict[str, Any]] = None,
                   ip_address: Optional[str] = None) -> AuditLog:
        db_obj = AuditLog(
            admin_id=admin_id,
            action=action,
            target_resource_id=target_resource_id,
            target_resource_type=target_resource_type,
            details=details,
            ip_address=ip_address
        )
        db.add(db_obj)
        db.commit()
        return db_obj

audit_repo = AuditRepository()
