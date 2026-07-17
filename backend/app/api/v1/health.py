from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import dependencies
from app.services.health_service import health_service

router = APIRouter()

@router.get("/ping")
def ping():
    """
    Simple liveness check - no DB dependency.
    Used by Railway/load balancer healthchecks.
    """
    return {"status": "ok"}

@router.get("/")
def get_health(db: Session = Depends(dependencies.get_db)):
    """
    Check the health of all backing services.
    Public endpoint for load balancers.
    """
    return health_service.check_health(db)
