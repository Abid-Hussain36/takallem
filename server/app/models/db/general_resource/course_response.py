from pydantic import BaseModel
from app.db.enums import AvailableCourse, AvailableDialect, AvailableLanguage


class CourseResponse(BaseModel):
    id: int
    course_name: AvailableCourse
    total_modules: int
    image: str
    text_color: str
    default_dialect: AvailableDialect | None = None
    language: AvailableLanguage