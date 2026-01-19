from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.db.schemas.user_course_progress import UserCourseProgress
from app.db.schemas.user import User
from app.models.db.user.user_course_progress_response import UserCourseProgressResponse
from app.models.general.success_message import SuccessMessage
from app.db.enums import AvailableCourse, AvailableDialect
from app.models.db.user.user_course_progress_requests.create_user_course_progress_request import CreateUserCourseProgressRequest
from app.models.db.user.user_course_progress_requests.update_user_course_progress_dialect_request import UpdateUserCourseProgressDialectRequest
from app.models.db.user.user_course_progress_requests.add_covered_word_request import AddCoveredWordReqest
from app.models.db.user.user_course_progress_requests.increment_current_vocab_problem_set_request import IncrementCurrentVocabProblemSetRequest


class UserCourseProgressService:
    def get_user_course_progress(
        self, 
        db: Session, 
        user_id: int,
        course: AvailableCourse
    ) -> UserCourseProgressResponse:
        """Gets the user-course-progress by user_id and course"""
        progress = db.query(UserCourseProgress).filter(
            UserCourseProgress.user_id == user_id,
            UserCourseProgress.course_name == course,
        ).first()
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course progress not found"
            )
        
        return progress.to_model()

    def create_user_course_progress(
        self,
        db: Session,
        createUserCourseProgressRequest: CreateUserCourseProgressRequest,
    ) -> UserCourseProgressResponse:
        """Creates a UserCourseProgress row for the user with the course and dialect"""
        user_id = createUserCourseProgressRequest.id
        course = createUserCourseProgressRequest.course
        default_dialect = createUserCourseProgressRequest.default_dialect
        total_modules = createUserCourseProgressRequest.total_modules

        # Check if the course already exists in progress for user
        existing = db.query(UserCourseProgress).filter(
            UserCourseProgress.user_id == user_id,
            UserCourseProgress.course_name == course
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User course progress already exists"
            )
        
        new_progress = UserCourseProgress(
            user_id=user_id,
            course_name=course,
            dialect=None,
            default_dialect=default_dialect,
            total_modules=total_modules,
            curr_module=1,
            covered_words={},
            problem_counter=0,
            current_vocab_problem_set=1
        )
        
        db.add(new_progress)
        db.commit()
        db.refresh(new_progress)
        
        return new_progress.to_model()

    def update_user_course_progress_dialect(self, db: Session, updateUserCourseProgressDialect: UpdateUserCourseProgressDialectRequest) -> UserCourseProgressResponse:
        user_id = updateUserCourseProgressDialect.id
        course = updateUserCourseProgressDialect.course
        dialect = updateUserCourseProgressDialect.dialect

        progress = db.query(UserCourseProgress).filter(
            UserCourseProgress.user_id == user_id,
            UserCourseProgress.course_name == course
        ).first()

        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course progress not found"
            )

        progress.dialect = dialect
        db.commit()
        db.refresh(progress)
        
        return progress.to_model()

    def increment_curr_module(self, db: Session, id: int) -> UserCourseProgressResponse:
        """Increments the curr_module by 1"""
        progress = db.query(UserCourseProgress).filter(UserCourseProgress.id == id).first()
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course progress not found"
            )
        
        progress.curr_module += 1
        db.commit()
        db.refresh(progress)
        
        return progress.to_model()

    def add_covered_word(self, db: Session, addCoveredWordRequest: AddCoveredWordReqest) -> UserCourseProgressResponse:
        """Updates covered_words based on the logic specified"""
        id = addCoveredWordRequest.id
        word = addCoveredWordRequest.word

        progress = db.query(UserCourseProgress).filter(UserCourseProgress.id == id).first()
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course progress not found"
            )
        
        # If word not in covered_words
        if word not in progress.covered_words:
            progress.covered_words[word] = 1
        # If word value is 1
        elif progress.covered_words[word] == 1:
            progress.covered_words[word] = 2
            progress.problem_counter += 1
        # If word value is 2, do nothing (already handled by not having else)
        
        db.commit()
        db.refresh(progress)
        
        return progress.to_model()

    def clear_covered_words(self, db: Session, id: int) -> UserCourseProgressResponse:
        """Clears the covered_words dictionary"""
        progress = db.query(UserCourseProgress).filter(UserCourseProgress.id == id).first()
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course progress not found"
            )
        
        progress.covered_words = {}
        db.commit()
        db.refresh(progress)
        
        return progress.to_model()

    def increment_problem_counter(self, db: Session, id: int) -> UserCourseProgressResponse:
        """Increments the problem_counter by 1"""
        progress = db.query(UserCourseProgress).filter(UserCourseProgress.id == id).first()
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course progress not found"
            )
        
        progress.problem_counter += 1
        db.commit()
        db.refresh(progress)
        
        return progress.to_model()

    def clear_problem_counter(self, db: Session, id: int) -> UserCourseProgressResponse:
        """Sets the problem_counter to 1"""
        progress = db.query(UserCourseProgress).filter(UserCourseProgress.id == id).first()
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course progress not found"
            )
        
        progress.problem_counter = 1
        db.commit()
        db.refresh(progress)
        
        return progress.to_model()

    def increment_current_vocab_problem_set(
        self, 
        db: Session, 
        incrementCurrentVocabProblemSetRequest: IncrementCurrentVocabProblemSetRequest
    ) -> UserCourseProgressResponse:
        """Increments or resets current_vocab_problem_set based on limit"""
        id = incrementCurrentVocabProblemSetRequest.id
        limit = incrementCurrentVocabProblemSetRequest.limit

        progress = db.query(UserCourseProgress).filter(UserCourseProgress.id == id).first()
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course progress not found"
            )
        
        if progress.current_vocab_problem_set == limit:
            progress.current_vocab_problem_set = 1
        else:
            progress.current_vocab_problem_set += 1
        
        db.commit()
        db.refresh(progress)
        
        return progress.to_model()

    def clear_current_vocab_problem_set(self, db: Session, id: int) -> UserCourseProgressResponse:
        """Sets current_vocab_problem_set to 1"""
        progress = db.query(UserCourseProgress).filter(UserCourseProgress.id == id).first()
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course progress not found"
            )
        
        progress.current_vocab_problem_set = 1
        db.commit()
        db.refresh(progress)
        
        return progress.to_model()

    def delete_user_course_progress(self, db: Session, id: int, course: AvailableCourse) -> SuccessMessage:
        """Deletes a UserCourseProgress row by id"""
        progress = db.query(UserCourseProgress).filter(
            UserCourseProgress.id == id,
            UserCourseProgress.course_name == course
        ).first()
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course progress not found"
            )
        
        db.delete(progress)
        db.commit()
        
        return SuccessMessage(message=f"User course progress for course {course} successfully deleted")
