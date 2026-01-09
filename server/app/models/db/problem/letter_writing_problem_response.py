from pydantic import BaseModel
from typing import List


class LetterWritingProblemResponse(BaseModel):
    id: int
    problem_set_id: int
    word: str
    position: str
    reference_writing: str
    writing_sequence: List[str]

