from typing import Union
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.models.db.user.user_response import UserResponse
from app.db.database import get_db
from app.models.auth.signup_request import SignupRequest
from app.services.user_service import UserService
from app.utils.di import get_user_service
from app.utils.auth import get_current_user_email
from app.models.general.error_message import ErrorMessage
from app.models.general.success_message import SuccessMessage
from app.db.enums import AvailableCourse, Gender, AvailableDialect


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
    email: str = Depends(get_current_user_email), # Takes in the header auth token and validates by fetching the user email
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


@user_router.delete("/{email}", response_model=SuccessMessage)
def delete_user(
    email: str, 
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> SuccessMessage:
    """Delete a user by email"""
    return service.delete_user_by_email(db, email)


@user_router.put("/{id}/current-course/{course}", response_model=UserResponse)
def update_current_course(
    id: int,
    course: AvailableCourse,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Updates the current course field for user"""
    return service.update_current_course(db, id, course)


@user_router.put("/{id}/current-dialect/{dialect}", response_model=UserResponse)
def update_current_dialect(
    id: int,
    dialect: AvailableDialect,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Updates the current dialect field for user"""
    return service.update_current_dialect(db, id, dialect)


@user_router.put("/{id}/language-learning/add/{language}", response_model=UserResponse)
def add_language_learning(
    id: int,
    language: str,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Adds a language to the user's language-learning list"""
    return service.add_language_learning(db, id, language)


@user_router.put("/{id}/language-learning/remove/{language}", response_model=UserResponse)
def remove_language_learning(
    id: int,
    language: str,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Removes a language from the user's language-learning list"""
    return service.remove_language_learning(db, id, language)


@user_router.put("/{id}/language-learned/add/{language}", response_model=UserResponse)
def add_language_learned(
    id: int,
    language: str,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Adds a language to the user's language-learned list"""
    return service.add_language_learned(db, id, language)


@user_router.put("/{id}/language-learned/remove/{language}", response_model=UserResponse)
def remove_language_learned(
    id: int,
    language: str,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Removes a language from the user's language-learned list"""
    return service.remove_language_learned(db, id, language)


@user_router.put("/{id}", response_model=UserResponse)
def update_user_profile(
    id: int,
    first_name: str | None = Query(None),
    last_name: str | None = Query(None),
    gender: Gender | None = Query(None),
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Updates user profile fields (first_name, last_name, gender)"""
    return service.update_user_profile(db, id, first_name, last_name, gender)
