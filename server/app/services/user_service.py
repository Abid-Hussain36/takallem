from typing import Union
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.schemas.user import User
from app.db.schemas.user_course_progress import UserCourseProgress
from app.models.auth.signup_request import SignupRequest
from app.models.db.user.user_response import UserResponse
from app.models.general.error_message import ErrorMessage
from app.models.general.success_message import SuccessMessage
from app.db.enums import AvailableCourse, Gender


class UserService:
    def create_user(self, db: Session, user_data: SignupRequest) -> UserResponse:
        """Creates a user based on the passed in signup data and authentication id"""
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            gender=user_data.gender,
            current_course=user_data.current_course,
            languages_learning=user_data.languages_learning or [],
            languages_learned=user_data.languages_learned or []
        )

        try:
            db.add(new_user) # Stage the adding of the new user
            db.commit() # Commit the change to the DB
            db.refresh(new_user) # Creates the ID and relationships needed for the new user
            return new_user.to_model()
        except IntegrityError as e:
            db.rollback() # Undo any changes we made if we have an error like user already existing
            raise ValueError("User with this email or username already exists")

    def get_user_by_email(self, db: Session, email: str) -> UserResponse | None:
        """Gets the user by email address"""
        user = db.query(User).filter(User.email == email).first()
        if user:
            return user.to_model() # The lazy load is triggered for progresses cause we access the relational field.
        return None

    def get_user_by_id(self, db: Session, user_id: int) -> UserResponse | None:
        """Gets the user by database ID"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            return user.to_model() # The lazy load is triggered for progresses cause we access the relational field.
        return None

    def delete_user_by_email(self, db: Session, email: str) -> SuccessMessage:
        """Deletes a user by their email"""
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise HTTPException(
                status=status.HTTP_404_NOT_FOUND,
                detail="User with email does not exist."
            )

        db.delete(user)
        db.commit()
        
        return SuccessMessage(message=f"User with email {email} successfully deleted")

    def update_current_course(self, db: Session, user_id: int, course: AvailableCourse) -> UserResponse:
        """Updates the current course for a user"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.current_course = course
        db.commit()
        db.refresh(user)
        
        return user.to_model()

    def add_language_learning(self, db: Session, user_id: int, language: str) -> UserResponse:
        """Adds a language to the user's language-learning list"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if language in user.languages_learning:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Language already in learning list"
            )
        
        user.languages_learning.append(language)
        db.commit()
        db.refresh(user)
        
        return user.to_model()

    def remove_language_learning(self, db: Session, user_id: int, language: str) -> UserResponse:
        """Removes a language from the user's language-learning list"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not user.languages_learning or language not in user.languages_learning:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Language not in learning list"
            )
        
        user.languages_learning.remove(language)
        db.commit()
        db.refresh(user)
        
        return user.to_model()

    def add_language_learned(self, db: Session, user_id: int, language: str) -> UserResponse:
        """Adds a language to the user's language-learned list"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if language in user.languages_learned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Language already in learned list"
            )
        
        user.languages_learned.append(language)
        db.commit()
        db.refresh(user)
        
        return user.to_model()

    def remove_language_learned(self, db: Session, user_id: int, language: str) -> UserResponse:
        """Removes a language from the user's language-learned list"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not user.languages_learned or language not in user.languages_learned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Language not in learned list"
            )
        
        user.languages_learned.remove(language)
        db.commit()
        db.refresh(user)
        
        return user.to_model()

    def update_user_profile(
        self, 
        db: Session, 
        user_id: int, 
        first_name: str | None = None,
        last_name: str | None = None,
        gender: Gender | None = None
    ) -> UserResponse:
        """Updates user profile fields"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if gender is not None:
            user.gender = gender
        
        db.commit()
        db.refresh(user)
        
        return user.to_model()
