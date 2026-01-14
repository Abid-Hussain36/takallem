from typing import Union
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.db.user.user_response import UserResponse
from app.db.database import get_db
from app.models.auth.signup_request import SignupRequest
from app.services.user_service import UserService
from app.utils.di import get_user_service
from app.utils.auth import get_current_user_email


user_router = APIRouter()


@user_router.post("/create", response_model=UserResponse)
def create_user(
    user_data: SignupRequest,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    return service.create_user(db, user_data)


@user_router.get("/me", response_model=UserResponse)
def get_authed_user(
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Get the currently authenticated user's profile by their email"""
    user = service.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user