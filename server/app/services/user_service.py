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
from app.db.enums import AvailableCourse, AvailableLanguage, Gender, AvailableDialect
from app.models.db.user.update_user_request import UpdateUserRequest


class UserService:
    def create_user(self, db: Session, user_data: SignupRequest) -> UserResponse:
        """Creates a user based on the passed in signup data. Used for Signup."""
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            gender=user_data.gender,
            current_course=user_data.current_course,
            current_dialect=user_data.current_dialect,
            languages_learning=user_data.languages_learning or [],
            languages_learned=user_data.languages_learned or [],
            courses_completed=user_data.courses_completed or []
        )

        try:
            db.add(new_user) # Stage the adding of the new user
            db.commit() # Commit the change to the DB
            db.refresh(new_user) # Creates the ID and relationships needed for the new user
            return new_user.to_model()
        except IntegrityError as e:
            db.rollback() # Undo any changes we made if we have an error like user already existing
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists"
            )


    def get_user_by_email(self, db: Session, email: str) -> UserResponse | None:
        """Gets the user by email address. Used for Login."""
        user = db.query(User).filter(User.email == email).first()
        if user:
            return user.to_model() # The lazy load is triggered for progresses cause we access the relational field.
        return None


    def get_authed_user(self, db: Session, email: str) -> UserResponse:
        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user.to_model()


    def update_user_profile(
        self, 
        db: Session, 
        email: str,
        updateUserRequest: UpdateUserRequest
    ) -> UserResponse:
        """Updates user profile fields"""
        first_name = updateUserRequest.first_name
        last_name = updateUserRequest.last_name
        gender = updateUserRequest.gender

        user = db.query(User).filter(User.email == email).first()
        
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


    def delete_user_by_email(self, db: Session, email: str) -> SuccessMessage:
        """Deletes a user by their email"""
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        db.delete(user)
        db.commit()
    
        return SuccessMessage(message=f"User with email {email} successfully deleted")


    def update_current_course(self, db: Session, email: str, course: AvailableCourse) -> UserResponse:
        """Updates the current course for a user"""
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.current_course = course
        db.commit()
        db.refresh(user)
        
        return user.to_model()


    def clear_current_course(self, db: Session, email: str) -> UserResponse:
        """Clears the current user course"""
        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user.current_course = None
        db.commit()
        db.refresh(user)

        return user.to_model()


    def update_current_dialect(self, db: Session, email: str, dialect: AvailableDialect) -> UserResponse:
        """Updates the current dialect for a user"""
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.current_dialect = dialect
        db.commit()
        db.refresh(user)
        
        return user.to_model()


    def clear_current_dialect(self, db: Session, email: str) -> UserResponse:
        """Clears the current dialect for a user"""
        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user.current_dialect = None
        db.commit()
        db.refresh(user)

        return user.to_model()


    def add_language_learning(self, db: Session, email: str, language: AvailableLanguage) -> UserResponse:
        """Adds a language to the user's language-learning list"""
        user = db.query(User).filter(User.email == email).first()
        
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


    def remove_language_learning(self, db: Session, email: str, language: AvailableLanguage) -> UserResponse:
        """Removes a language from the user's language-learning list"""
        user = db.query(User).filter(User.email == email).first()
        
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


    def add_language_learned(self, db: Session, email: str, language: AvailableLanguage) -> UserResponse:
        """Adds a language to the user's language-learned list"""
        user = db.query(User).filter(User.email == email).first()
        
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


    def remove_language_learned(self, db: Session, email: str, language: AvailableLanguage) -> UserResponse:
        """Removes a language from the user's language-learned list"""
        user = db.query(User).filter(User.email == email).first()
        
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
    

    def add_course_completed(self, db: Session, email: str, course: AvailableCourse) -> UserResponse:
        """Adds a course to the user's courses-completed list"""
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if course in user.courses_completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course already in completed list"
            )
        
        user.courses_completed.append(course)
        db.commit()
        db.refresh(user)
        
        return user.to_model()


    def remove_course_completed(self, db: Session, email: str, course: AvailableCourse) -> UserResponse:
        """Removes a course from the user's courses-completed list"""
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not user.courses_completed or course not in user.courses_completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course not in completed list"
            )
        
        user.courses_completed.remove(course)
        db.commit()
        db.refresh(user)
        
        return user.to_model()