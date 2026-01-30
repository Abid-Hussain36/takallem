from pydantic import BaseModel
from typing import Dict
from app.db.enums import AvailableCourse, AvailableDialect, AvailableLanguage


class UserCourseProgressResponse(BaseModel):
    id: int
    course_name: AvailableCourse
    language: AvailableLanguage
    dialect: AvailableDialect | None = None
    default_dialect: AvailableDialect | None = None
    total_modules: int
    curr_module: int
    covered_words: Dict[str, int]
    problem_counter: int
    current_vocab_problem_set: int