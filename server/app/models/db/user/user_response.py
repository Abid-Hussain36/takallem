from pydantic import BaseModel
from typing import List
from app.models.db.user.user_course_progress_response import UserCourseProgressResponse


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str | None = None
    languages_learning: List[str]
    course_progresses: List[UserCourseProgressResponse]