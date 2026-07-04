from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.api import dependencies
from app.repositories.user_repo import user_repo
from app.services.user_service import user_service
from app.schemas.user import UserRead, UserCreate, UserUpdate, PasswordChange
from app.core.permissions import Permission
from app.models.user import User
from app.core.security import verify_password

router = APIRouter()

@router.get("/me", response_model=UserRead)
def read_user_me(
    current_user: User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.post("/change-password")
def change_password(
    password_change: PasswordChange,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Change user password. Forces unsetting `force_password_change`.
    """
    if not verify_password(password_change.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid current password")
    
    user_update = UserUpdate(password=password_change.new_password)
    user_repo.update(db, db_obj=current_user, obj_in=user_update)
    return {"message": "Password updated successfully"}

@router.get("/", response_model=List[UserRead])
def read_users(
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(dependencies.require_permission(Permission.READ_USERS))
) -> Any:
    """
    Retrieve users (Admin only).
    """
    users = user_repo.get_multi(db, skip=skip, limit=limit)
    return users

from app.services.email_service import email_service

@router.post("/", response_model=UserRead)
def create_user(
    *,
    db: Session = Depends(dependencies.get_db),
    user_in: UserCreate,
    current_user: User = Depends(dependencies.require_permission(Permission.CREATE_USER))
) -> Any:
    """
    Create new user (Admin only).
    """
    # Check if user already exists
    if user_repo.get_by_email(db, email=user_in.email):
        raise HTTPException(status_code=400, detail="User with this email already exists")
        
    user = user_service.create_user(db=db, user_in=user_in)
    
    # Send welcome email with temporary password
    try:
        email_service.send_welcome_email(user_in.email, user_in.password)
    except Exception as e:
        # We don't want to fail the user creation if email fails, but we should log it
        import logging
        logging.getLogger(__name__).error(f"Failed to send welcome email: {e}")
        
    return user

@router.delete("/{user_id}", response_model=UserRead)
def delete_user(
    *,
    db: Session = Depends(dependencies.get_db),
    user_id: UUID,
    current_user: User = Depends(dependencies.require_permission(Permission.DELETE_USER)),
) -> Any:
    """
    Delete a user (Admin only).
    """
    user = user_repo.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = user_repo.delete(db, user_id=user_id)
    return user
