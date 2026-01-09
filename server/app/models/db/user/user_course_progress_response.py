from pydantic import BaseModel
from typing import Dict
from app.db.enums import Course


class UserCourseProgressResponse(BaseModel):
    id: int
    course_name: Course
    dialect: str | None = None
    curr_module: int
    covered_words: Dict[str, int]
    problem_counter: int
    current_vocab_problem_set: int