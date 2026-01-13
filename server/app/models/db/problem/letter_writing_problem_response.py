from pydantic import BaseModel
from typing import List
from app.models.db.lecture.letter_writing_sequence_response import LetterWritingSequenceResponse


class LetterWritingProblemResponse(BaseModel):
    id: int
    problem_set_id: int
    letter: str
    position: str
    reference_writing: str
    writing_sequence: LetterWritingSequenceResponse

