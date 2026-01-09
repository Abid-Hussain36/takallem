from pydantic import BaseModel
from typing import List
from app.db.enums import ResourceType


class LetterWritingLectureResponse(BaseModel):
    id: int
    resource_type: ResourceType
    letter: str
    content: List[str]
    letter_writing_sequence: List[str]

