from pydantic import BaseModel
from typing import List
from app.db.enums import AvailableLanguage
from app.models.db.general_resource.dialect_response import DialectResponse
from app.models.db.general_resource.course_response import CourseResponse


class LanguageResponse(BaseModel):
    id: int
    language: AvailableLanguage
    image: str
    text_color: str
    dialects: List[DialectResponse]
    courses: List[CourseResponse]