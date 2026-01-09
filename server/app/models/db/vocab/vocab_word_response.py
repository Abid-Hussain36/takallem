from pydantic import BaseModel
from app.db.enums import Course


class VocabWordResponse(BaseModel):
    id: int
    lecture_id: int
    word: str
    meaning: str
    course: Course
    language: str
    dialect: str | None = None
    vocab_audio: str

