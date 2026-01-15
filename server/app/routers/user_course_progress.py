from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.db.user.user_course_progress_response import UserCourseProgressResponse
from app.db.database import get_db
from app.services.user_course_progress_service import UserCourseProgressService
from app.utils.di import get_user_course_progress_service
from app.models.general.success_message import SuccessMessage
from app.db.enums import AvailableCourse


user_course_progress_router = APIRouter()


@user_course_progress_router.get("/{user_id}/{course}/{dialect}", response_model=UserCourseProgressResponse)
def get_user_course_progress(
    user_id: int,
    course: AvailableCourse,
    dialect: str | None,
    db: Session = Depends(get_db),
    service: UserCourseProgressService = Depends(get_user_course_progress_service)
) -> UserCourseProgressResponse:
    """Gets the user-course-progress by user_id, course, and dialect"""
    return service.get_user_course_progress(db, user_id, course, dialect)


@user_course_progress_router.post("/{user_id}/{course}/{dialect}", response_model=UserCourseProgressResponse)
def create_user_course_progress(
    user_id: int,
    course: AvailableCourse,
    dialect: str | None,
    db: Session = Depends(get_db),
    service: UserCourseProgressService = Depends(get_user_course_progress_service)
) -> UserCourseProgressResponse:
    """Creates a UserCourseProgress row for the user with the course and dialect"""
    return service.create_user_course_progress(db, user_id, course, dialect)


@user_course_progress_router.put("/{id}/curr_module/increment", response_model=UserCourseProgressResponse)
def increment_curr_module(
    id: int,
    db: Session = Depends(get_db),
    service: UserCourseProgressService = Depends(get_user_course_progress_service)
) -> UserCourseProgressResponse:
    """Increments the curr_module by 1"""
    return service.increment_curr_module(db, id)


@user_course_progress_router.put("/{id}/covered_words/{word}", response_model=UserCourseProgressResponse)
def update_covered_words(
    id: int,
    word: str,
    db: Session = Depends(get_db),
    service: UserCourseProgressService = Depends(get_user_course_progress_service)
) -> UserCourseProgressResponse:
    """Updates covered_words based on word count logic"""
    return service.update_covered_words(db, id, word)


@user_course_progress_router.put("/{id}/covered_words/clear", response_model=UserCourseProgressResponse)
def clear_covered_words(
    id: int,
    db: Session = Depends(get_db),
    service: UserCourseProgressService = Depends(get_user_course_progress_service)
) -> UserCourseProgressResponse:
    """Clears the covered_words dictionary"""
    return service.clear_covered_words(db, id)


@user_course_progress_router.put("/{id}/problem_counter/increment", response_model=UserCourseProgressResponse)
def increment_problem_counter(
    id: int,
    db: Session = Depends(get_db),
    service: UserCourseProgressService = Depends(get_user_course_progress_service)
) -> UserCourseProgressResponse:
    """Increments the problem_counter by 1"""
    return service.increment_problem_counter(db, id)


@user_course_progress_router.put("/{id}/problem_counter/clear", response_model=UserCourseProgressResponse)
def clear_problem_counter(
    id: int,
    db: Session = Depends(get_db),
    service: UserCourseProgressService = Depends(get_user_course_progress_service)
) -> UserCourseProgressResponse:
    """Sets the problem_counter to 1"""
    return service.clear_problem_counter(db, id)


@user_course_progress_router.put("/{id}/current_vocab_problem_set/increment/{limit}", response_model=UserCourseProgressResponse)
def increment_current_vocab_problem_set(
    id: int,
    limit: int,
    db: Session = Depends(get_db),
    service: UserCourseProgressService = Depends(get_user_course_progress_service)
) -> UserCourseProgressResponse:
    """Increments or resets current_vocab_problem_set based on limit"""
    return service.increment_current_vocab_problem_set(db, id, limit)


@user_course_progress_router.put("/{id}/current_vocab_problem_set/clear", response_model=UserCourseProgressResponse)
def clear_current_vocab_problem_set(
    id: int,
    db: Session = Depends(get_db),
    service: UserCourseProgressService = Depends(get_user_course_progress_service)
) -> UserCourseProgressResponse:
    """Sets current_vocab_problem_set to 1"""
    return service.clear_current_vocab_problem_set(db, id)


@user_course_progress_router.delete("/{id}", response_model=SuccessMessage)
def delete_user_course_progress(
    id: int,
    db: Session = Depends(get_db),
    service: UserCourseProgressService = Depends(get_user_course_progress_service)
) -> SuccessMessage:
    """Deletes a UserCourseProgress row by id"""
    return service.delete_user_course_progress(db, id)
