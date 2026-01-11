from pydantic import BaseModel
from typing import List
from app.models.db.user.user_course_progress_response import UserCourseProgressResponse
from app.db.enums import AvailableCourse, Gender


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str | None = None
    gender: Gender
    current_course: AvailableCourse
    languages_learning: List[str]
    course_progresses: List[UserCourseProgressResponse]