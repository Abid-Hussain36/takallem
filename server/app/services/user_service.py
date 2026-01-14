from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.schemas.user import User
from app.db.schemas.user_course_progress import UserCourseProgress
from app.models.auth.signup_request import SignupRequest
from app.models.db.user.user_response import UserResponse


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
            languages_learning=user_data.languages_learning or []
        )

        try:
            db.add(new_user) # Stage the adding of the new user
            db.commit() # Commit the change to the DB
            db.refresh(new_user) # Creates the ID and relationships needed for the new user
            return new_user.to_model()
        except IntegrityError as e:
            db.rollback() # Undo any changes we made if we have an error like user already existing
            raise ValueError("User with this email or username already exists")

    
    def get_user_by_id(self, db: Session, id: int) -> UserResponse | None:
        """Gets the user by id"""
        user = db.query(User).filter(User.id == id).first()
        if user:
            return user.to_model() # The lazy load is triggered for progresses cause we access the relational field.
        return None