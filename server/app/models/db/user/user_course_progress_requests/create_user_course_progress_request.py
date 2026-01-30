from pydantic import BaseModel
from app.db.enums import AvailableCourse, AvailableDialect, AvailableLanguage


class CreateUserCourseProgressRequest(BaseModel):
    id: int
    course: AvailableCourse
    language: AvailableLanguage
    default_dialect: AvailableDialect | None
    total_modules: int