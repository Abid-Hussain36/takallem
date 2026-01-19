from pydantic import BaseModel
from app.db.enums import AvailableCourse, AvailableDialect


class CreateUserCourseProgressRequest(BaseModel):
    id: int
    course: AvailableCourse
    default_dialect: AvailableDialect | None
    total_modules: int