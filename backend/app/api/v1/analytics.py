from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import dependencies
from app.models.user import User
from app.services.analytics_service import analytics_service
from app.core.permissions import has_permission, Permission
import csv
from io import StringIO
from fastapi.responses import StreamingResponse

router = APIRouter()

def check_analytics_permission(current_user: User = Depends(dependencies.get_current_active_user)):
    if not has_permission(current_user.role, Permission.VIEW_ANALYTICS):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

@router.get("/overview")
def get_overview(
    db: Session = Depends(dependencies.get_db),
    user: User = Depends(check_analytics_permission)
):
    return analytics_service.get_overview(db)

@router.get("/export")
def export_analytics(
    db: Session = Depends(dependencies.get_db),
    user: User = Depends(check_analytics_permission)
):
    data = analytics_service.get_overview(db)
    
    # Simple CSV export logic
    f = StringIO()
    writer = csv.writer(f)
    writer.writerow(["Category", "Metric", "Value"])
    
    for category, metrics in data.items():
        for k, v in metrics.items():
            writer.writerow([category, k, v])
            
    f.seek(0)
    response = StreamingResponse(iter([f.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=analytics_export.csv"
    return response
