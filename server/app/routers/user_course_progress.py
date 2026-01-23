from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.models.db.user.user_course_progress_response import UserCourseProgressResponse
from app.db.database import get_db
from app.services.user_course_progress_service import UserCourseProgressService
from app.utils.di import get_user_course_progress_service
from app.models.general.success_message import SuccessMessage
from app.db.enums import AvailableCourse, AvailableDialect
from app.utils.auth import get_current_user_email
from app.models.db.user.user_course_progress_requests.create_user_course_progress_request import CreateUserCourseProgressRequest
from app.models.db.user.user_course_progress_requests.update_user_course_progress_dialect_request import UpdateUserCourseProgressDialectRequest
from app.models.db.user.user_course_progress_requests.add_covered_word_request import AddCoveredWordReqest
from app.models.db.user.user_course_progress_requests.increment_current_vocab_problem_set_request import IncrementCurrentVocabProblemSetRequest
from app.models.db.user.user_course_progress_requests.add_covered_word_response import AddCoveredWordResponse


user_course_progress_router = APIRouter()


@user_course_progress_router.get("/", response_model=UserCourseProgressResponse)
def get_user_course_progress(
    user_id: int = Query(),
    course: AvailableCourse = Query(),
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserCourseProgressService = Depends(get_user_course_progress_service)
) -> UserCourseProgressResponse:
    """Gets the user-course-progress by user_id, course, and dialect"""
    return service.get_user_course_progress(db, user_id, course)


@user_course_progress_router.post("/", response_model=UserCourseProgressResponse)
def create_user_course_progress(
    createUserCourseProgressRequest: CreateUserCourseProgressRequest,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserCourseProgressService = Depends(get_user_course_progress_service)
) -> UserCourseProgressResponse:
    """
        Creates a UserCourseProgress row for the user with the course and the default dialect for the course.
        The actual dialect the user chooses will be stored later on
    """
    return service.create_user_course_progress(db, createUserCourseProgressRequest)


@user_course_progress_router.delete("/{id}/{course}", response_model=SuccessMessage)
def delete_user_course_progress(
    id: int,
    course: AvailableCourse,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserCourseProgressService = Depends(get_user_course_progress_service)
) -> SuccessMessage:
    """Deletes a UserCourseProgress row by id"""
    return service.delete_user_course_progress(db, id, course)


@user_course_progress_router.put("/dialect", response_model=UserCourseProgressResponse)
def update_user_course_progress_dialect(
    updateUserCourseProgressDialect: UpdateUserCourseProgressDialectRequest,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserCourseProgressService = Depends(get_user_course_progress_service)
):
    """Updates the dialect field of the progress object."""
    return service.update_user_course_progress_dialect(db, updateUserCourseProgressDialect)


@user_course_progress_router.put("/curr_module/increment/{id}", response_model=UserCourseProgressResponse)
def increment_curr_module(
    id: int,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserCourseProgressService = Depends(get_user_course_progress_service)
) -> UserCourseProgressResponse:
    """Increments the curr_module by 1"""
    return service.increment_curr_module(db, id)


@user_course_progress_router.put("/covered_words", response_model=AddCoveredWordResponse)
def add_covered_word(
    addCoveredWordRequest: AddCoveredWordReqest,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserCourseProgressService = Depends(get_user_course_progress_service)
) -> AddCoveredWordResponse:
    """Updates covered_words based on word count logic"""
    return service.add_covered_word(db, addCoveredWordRequest)


@user_course_progress_router.put("/covered_words/clear/{id}", response_model=UserCourseProgressResponse)
def clear_covered_words(
    id: int,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserCourseProgressService = Depends(get_user_course_progress_service)
) -> UserCourseProgressResponse:
    """Clears the covered_words dictionary"""
    return service.clear_covered_words(db, id)


@user_course_progress_router.put("/problem_counter/increment/{id}", response_model=UserCourseProgressResponse)
def increment_problem_counter(
    id: int,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserCourseProgressService = Depends(get_user_course_progress_service)
) -> UserCourseProgressResponse:
    """Increments the problem_counter by 1"""
    return service.increment_problem_counter(db, id)


@user_course_progress_router.put("/problem_counter/clear/{id}", response_model=UserCourseProgressResponse)
def clear_problem_counter(
    id: int,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserCourseProgressService = Depends(get_user_course_progress_service)
) -> UserCourseProgressResponse:
    """Sets the problem_counter to 1"""
    return service.clear_problem_counter(db, id)


@user_course_progress_router.put("/current_vocab_problem_set/increment", response_model=UserCourseProgressResponse)
def increment_current_vocab_problem_set(
    incrementCurrentVocabProblemSetRequest: IncrementCurrentVocabProblemSetRequest,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserCourseProgressService = Depends(get_user_course_progress_service)
) -> UserCourseProgressResponse:
    """Increments or resets current_vocab_problem_set based on limit"""
    return service.increment_current_vocab_problem_set(db, incrementCurrentVocabProblemSetRequest)


@user_course_progress_router.put("/current_vocab_problem_set/clear/{id}", response_model=UserCourseProgressResponse)
def clear_current_vocab_problem_set(
    id: int,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: UserCourseProgressService = Depends(get_user_course_progress_service)
) -> UserCourseProgressResponse:
    """Sets current_vocab_problem_set to 1"""
    return service.clear_current_vocab_problem_set(db, id)
