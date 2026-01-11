from pydantic import BaseModel
from app.db.enums import AvailableCourse


class VocabWordResponse(BaseModel):
    id: int
    lecture_id: int
    number: int
    word: str
    meaning: str
    course: AvailableCourse
    language: str
    dialect: str | None = None
    vocab_audio: str

