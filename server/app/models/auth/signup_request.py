from typing import List
from pydantic import BaseModel
from app.db.enums import Gender, AvailableCourse, AvailableDialect


class SignupRequest(BaseModel):
    email: str
    password: str
    username: str
    first_name: str
    last_name: str | None = None
    gender: Gender
    current_course: AvailableCourse | None = None
    current_dialect: AvailableDialect | None = None
    languages_learning: List[str] = []
    languages_learned: List[str] = []