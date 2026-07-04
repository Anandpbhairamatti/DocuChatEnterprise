from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.user_repo import user_repo
from app.schemas.user import UserCreate
from app.models.user import User

class UserService:
    def create_user(self, db: Session, user_in: UserCreate) -> User:
        # Check if email exists
        user = user_repo.get_by_email(db, email=user_in.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this email already exists in the system.",
            )
        return user_repo.create(db, obj_in=user_in)

user_service = UserService()
