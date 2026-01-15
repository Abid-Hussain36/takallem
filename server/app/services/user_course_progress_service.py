from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.db.schemas.user_course_progress import UserCourseProgress
from app.models.db.user.user_course_progress_response import UserCourseProgressResponse
from app.models.general.success_message import SuccessMessage
from app.db.enums import AvailableCourse
from app.utils.module_count_map import module_count_map


class UserCourseProgressService:
    def get_user_course_progress(
        self, 
        db: Session, 
        user_id: int, 
        course: AvailableCourse, 
        dialect: str | None
    ) -> UserCourseProgressResponse:
        """Gets the user-course-progress by user_id, course, and dialect"""
        progress = db.query(UserCourseProgress).filter(
            UserCourseProgress.user_id == user_id,
            UserCourseProgress.course_name == course,
            UserCourseProgress.dialect == dialect
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
        user_id: int,
        course: AvailableCourse,
        dialect: str | None
    ) -> UserCourseProgressResponse:
        """Creates a UserCourseProgress row for the user with the course and dialect"""
        # Check if already exists
        existing = db.query(UserCourseProgress).filter(
            UserCourseProgress.user_id == user_id,
            UserCourseProgress.course_name == course,
            UserCourseProgress.dialect == dialect
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User course progress already exists"
            )
        
        # Get total modules from module count map
        total_modules = module_count_map.get(course)
        if total_modules is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Course {course} not found in module count map"
            )
        
        new_progress = UserCourseProgress(
            user_id=user_id,
            course_name=course,
            dialect=dialect,
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

    def increment_curr_module(self, db: Session, progress_id: int) -> UserCourseProgressResponse:
        """Increments the curr_module by 1"""
        progress = db.query(UserCourseProgress).filter(UserCourseProgress.id == progress_id).first()
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course progress not found"
            )
        
        progress.curr_module += 1
        db.commit()
        db.refresh(progress)
        
        return progress.to_model()

    def update_covered_words(self, db: Session, progress_id: int, word: str) -> UserCourseProgressResponse:
        """Updates covered_words based on the logic specified"""
        progress = db.query(UserCourseProgress).filter(UserCourseProgress.id == progress_id).first()
        
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

    def clear_covered_words(self, db: Session, progress_id: int) -> UserCourseProgressResponse:
        """Clears the covered_words dictionary"""
        progress = db.query(UserCourseProgress).filter(UserCourseProgress.id == progress_id).first()
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course progress not found"
            )
        
        progress.covered_words = {}
        db.commit()
        db.refresh(progress)
        
        return progress.to_model()

    def increment_problem_counter(self, db: Session, progress_id: int) -> UserCourseProgressResponse:
        """Increments the problem_counter by 1"""
        progress = db.query(UserCourseProgress).filter(UserCourseProgress.id == progress_id).first()
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course progress not found"
            )
        
        progress.problem_counter += 1
        db.commit()
        db.refresh(progress)
        
        return progress.to_model()

    def clear_problem_counter(self, db: Session, progress_id: int) -> UserCourseProgressResponse:
        """Sets the problem_counter to 1"""
        progress = db.query(UserCourseProgress).filter(UserCourseProgress.id == progress_id).first()
        
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
        progress_id: int, 
        limit: int
    ) -> UserCourseProgressResponse:
        """Increments or resets current_vocab_problem_set based on limit"""
        progress = db.query(UserCourseProgress).filter(UserCourseProgress.id == progress_id).first()
        
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

    def clear_current_vocab_problem_set(self, db: Session, progress_id: int) -> UserCourseProgressResponse:
        """Sets current_vocab_problem_set to 1"""
        progress = db.query(UserCourseProgress).filter(UserCourseProgress.id == progress_id).first()
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course progress not found"
            )
        
        progress.current_vocab_problem_set = 1
        db.commit()
        db.refresh(progress)
        
        return progress.to_model()

    def delete_user_course_progress(self, db: Session, progress_id: int) -> SuccessMessage:
        """Deletes a UserCourseProgress row by id"""
        progress = db.query(UserCourseProgress).filter(UserCourseProgress.id == progress_id).first()
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course progress not found"
            )
        
        db.delete(progress)
        db.commit()
        
        return SuccessMessage(message=f"User course progress with id {progress_id} successfully deleted")
