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
from app.db.enums import AvailableCourse, AvailableLanguage, Gender, AvailableDialect
from app.models.db.user.update_user_request import UpdateUserRequest


user_router = APIRouter()


@user_router.get("/me", response_model=UserResponse)
def get_authed_user(
    email: str = Depends(get_current_user_email), # Takes in the header auth token and validates by fetching the user email
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Get the currently authenticated user's profile by their email"""
    return service.get_authed_user(db, email)


@user_router.put("/me", response_model=UserResponse)
def update_user_profile(
    updateUserRequest: UpdateUserRequest,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Updates user profile fields (first_name, last_name, gender)"""
    return service.update_user_profile(db, email, updateUserRequest)


@user_router.delete("/me", response_model=SuccessMessage)
def delete_user(
    email: str = Depends(get_current_user_email), 
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> SuccessMessage:
    """Delete a user by email"""
    return service.delete_user_by_email(db, email)


@user_router.put("/current-course/update/{course}", response_model=UserResponse)
def update_current_course(
    course: AvailableCourse,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Updates the current course field for user"""
    return service.update_current_course(db, email, course)


@user_router.put("/current-course/clear", response_model=UserResponse)
def clear_current_course(
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Clears the current course field for user"""
    return service.clear_current_course(db, email)


@user_router.put("/current-dialect/update/{dialect}", response_model=UserResponse)
def update_current_dialect(
    dialect: AvailableDialect,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Updates the current dialect field for user"""
    return service.update_current_dialect(db, email, dialect)


@user_router.put("/current-dialect/clear", response_model=UserResponse)
def clear_current_dialect(
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Clears the current dialect for the user"""
    service.clear_current_dialect(db, email)


@user_router.put("/language-learning/add/{language}", response_model=UserResponse)
def add_language_learning(
    language: AvailableLanguage,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Adds a language to the user's language-learning list"""
    return service.add_language_learning(db, email, language)


@user_router.put("/language-learning/remove/{language}", response_model=UserResponse)
def remove_language_learning(
    language: AvailableLanguage,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Removes a language from the user's language-learning list"""
    return service.remove_language_learning(db, email, language)


@user_router.put("/language-learned/add/{language}", response_model=UserResponse)
def add_language_learned(
    language: AvailableLanguage,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Adds a language to the user's language-learned list"""
    return service.add_language_learned(db, email, language)


@user_router.put("/language-learned/remove/{language}", response_model=UserResponse)
def remove_language_learned(
    language: AvailableLanguage,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Removes a language from the user's language-learned list"""
    return service.remove_language_learned(db, email, language)


@user_router.put("/course-completed/add/{course}", response_model=UserResponse)
def add_course_completed(
    course: AvailableCourse,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Adds a course to the user's courses-completed list"""
    return service.add_course_completed(db, email, course)


@user_router.put("/course-completed/remove/{course}", response_model=UserResponse)
def remove_course_completed(
    course: AvailableCourse,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Removes a course from the user's courses-completed list"""
    return service.remove_course_completed(db, email, course)