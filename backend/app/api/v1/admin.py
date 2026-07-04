from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import dependencies
from app.models.user import User
from app.repositories.audit_repo import audit_repo
from app.core.permissions import Permission
from app.models.audit_log import AuditLog
from typing import List, Any

router = APIRouter()

@router.get("/audit-logs")
def get_audit_logs(
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(dependencies.require_permission(Permission.VIEW_AUDIT_LOGS))
):
    """
    Retrieve audit logs for administrative oversight.
    """
    audit_repo.create_log(
        db=db,
        admin_id=current_user.id,
        action="VIEWED_AUDIT_LOGS"
    )
    # Return simple list of dicts for now
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    return logs

@router.post("/system-alerts/test")
def trigger_test_alert(
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.require_permission(Permission.MANAGE_SYSTEM_ALERTS))
):
    from app.models.system_alert import SystemAlert
    alert = SystemAlert(severity="WARNING", source="Admin Dashboard", message="Test alert triggered manually.")
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    audit_repo.create_log(db, admin_id=current_user.id, action="TRIGGERED_TEST_ALERT")
    return {"message": "Alert created successfully"}
