from pydantic import BaseModel
from typing import List
from app.db.enums import ResourceType
from app.models.db.lecture.letter_writing_sequence_response import LetterWritingSequenceResponse


class LetterWritingLectureResponse(BaseModel):
    id: int
    resource_type: ResourceType
    letter: str
    content: List[str]
    letter_writing_sequences: List[LetterWritingSequenceResponse]

